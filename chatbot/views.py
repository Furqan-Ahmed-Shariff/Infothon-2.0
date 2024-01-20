import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import json
import markdown
import requests
import os

api_key = os.getenv("AbstractApi")


api_url = "https://ipgeolocation.abstractapi.com/v1/?api_key=" + api_key

places_key = os.getenv("places_key")
places_host = os.getenv("places_host")
places_url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJrTLr-GyuEmsRBfy61i59si0&fields=address_components&key=AIzaSyCtGXVu49dbt39PczKrIzJbAwdVzG5oGPs "
places_headers = {
    "X-RapidAPI-Key": places_key,
    "X-RapidAPI-Host": places_host,
}

GOOGLE_API_KEY = "AIzaSyCAks_8sofyC_iw0x15LldN1oH05CuY7Xg"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")
language_codes = {
    "Hindi": "hi",
    "Kannada": "kn",
    "English": "en",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
}
languages = list(language_codes.keys())


def language_select(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["language"] = data["language"]
        return JsonResponse({"changed_language": request.session["language"]})


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


def to_json(message):
    message = message.replace("**", " ")
    return json.dumps({"response": message})


def get_ip_geolocation_data(ip_address):
    response = requests.get(api_url + "&ip_address=" + ip_address)

    return response.content


def get_ip(request):
    # g = GeoIP2()
    remote_addr = request.META.get("HTTP_X_FORWARDED_FOR")
    if remote_addr:
        address = remote_addr.split(",")[-1].strip()
    else:
        address = request.META.get("REMOTE_ADDR")
    # country = g.country("103.2.232.250")
    country = get_ip_geolocation_data("103.2.232.250").decode()
    country = json.loads(country)
    long = country["longitude"]
    lat = country["latitude"]
    return (lat, long, country["country_code"])


def loc_services(request):
    language = None
    if not request.session.get("language"):
        language = "Select Language"
    else:
        language = request.session.get("language")
    if request.method == "POST":
        (lat, long, code) = get_ip(request)
        query = json.loads(request.body).get("query")
        querystring = {
            "query": query,
            "lat": lat,
            "lng": long,
            "limit": "20",
            "language": language_codes[request.session["language"]],
            "region": code,
        }
        response = requests.get(
            places_url, headers=places_headers, params=querystring
        ).json()
        return JsonResponse(response)
    return render(
        request,
        "chatbot/nearby.html",
        {"languages": languages, "selected_lang": language},
    )


def translate(message, fr, to):
    import requests, uuid, json

    key = "ac3721230fce45cab64c882c961f7a08"
    endpoint = "https://api.cognitive.microsofttranslator.com"

    location = "centralindia"

    path = "/translate"
    constructed_url = endpoint + path

    params = {
        "api-version": "3.0",
        "from": fr,
        "to": to,
    }

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": message}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    return json.dumps(
        response,
        sort_keys=True,
        ensure_ascii=False,
        indent=4,
        separators=(",", ": "),
    )


def ask_gemini(message, request):
    if request.session["language"] != "English":
        message = translate(message, language_codes[request.session["language"]], "en")
        message = eval(message)
        message = message[0]["translations"][0]["text"]
    response = model.generate_content(message, stream=True)
    res = ""
    for chunk in response:
        if request.session["language"] != "English":
            final = translate(
                chunk.text, "en", language_codes[request.session["language"]]
            )
            final = eval(final)
            final = final[0]["translations"][0]["text"]
            res += final
            markdown_chunk = markdown.markdown(to_markdown(res).data)
            yield markdown_chunk
            continue
        res += chunk.text
        markdown_chunk = markdown.markdown(to_markdown(res).data)
        yield markdown_chunk


def chatbot(request):
    # chats = Chat.objects.filter(user=request.user)
    language = None
    if not request.session.get("language"):
        language = "Select Language"
    else:
        language = request.session.get("language")

    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_gemini(message, request)

        chat = Chat(
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now,
        )
        chat.save()
        return StreamingHttpResponse(response, content_type="text/event-stream")
    print(language)
    return render(
        request,
        "chatbot/chatbot.html",
        {"languages": languages, "selected_lang": language},
    )


def home(request):
    return render(request, "chatbot/index.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("chatbot")
        else:
            error_message = "Invalid username or password"
            return render(
                request,
                "chatbot/login.html",
                {"error_message": error_message},
            )
    else:
        return render(request, "chatbot/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect("chatbot")
            except:
                error_message = "Error creating account"
            return render(
                request,
                "chatbot/register.html",
                {"error_message": error_message},
            )
        else:
            error_message = "Password don't match"
            return render(
                request,
                "chatbot/register.html",
                {"error_message": error_message},
            )
    return render(request, "chatbot/register.html")


def logout(request):
    auth.logout(request)
    return redirect("login")
