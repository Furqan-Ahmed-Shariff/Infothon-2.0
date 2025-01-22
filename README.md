# Multilingual Chatbot for Indian Languages

This repository contains the base implementation of a multilingual chatbot designed to support conversations in various Indian languages. The project integrates the **Gemini API** and **Azure Translate Services** to provide seamless communication across languages.

---

## 🚀 Features

- **Multilingual Support:** Handles conversations in multiple Indian languages.
- **Gemini API Integration:** Leverages Gemini API for natural language understanding and chatbot responses.
- **Azure Translate Services:** Translates user input and chatbot responses to ensure smooth communication in any supported language.
- **Extensible Design:** Can be customized and extended for additional use cases.

---

## ⚙️ How It Works

1. **User Input:** Accepts input from the user in any supported Indian language.
2. **Translation:** Uses Azure Translate Services to convert the input into a default language (e.g., English) for processing.
3. **Chatbot Response:**
   - Processes the translated input via the Gemini API to generate an appropriate response.
4. **Translation Back:** Converts the chatbot's response back into the user's original language using Azure Translate.
5. **Output:** Returns the translated response to the user.

---

## 🛠️ Technologies Used

- **Gemini API:** For advanced NLP and response generation.
- **Azure Cognitive Services:** Specifically Azure Translate for language translation.
- **Python:** Core programming language for integration and logic.
- **Flask/Django (Optional):** For creating the backend interface if hosted as a web service.

---

## 📄 Requirements

- Python 3.8+
- API keys for:
  - [Gemini API](https://gemini.api.link)
  - [Azure Translate Services](https://azure.microsoft.com/en-us/services/cognitive-services/translator/)
 
## API Testing

-The gemini API and Azure Translate APIs were tested in a sample project at: https://github.com/Furqan-Ahmed-Shariff/base-for-chatbot
