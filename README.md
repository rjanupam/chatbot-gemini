# A Chabot powered by Gemini AI

## Assistant

- Apart from text input, the Chatbot can take voice input and image input.
- It provides text responses.
- To get voice responses, TTS (Text to Speech) is used.
- It has options to switch languages. Idk why!

## Run

- API key

  - Sign in to (Google AI Studio)[https://ai.google.dev]
  - Create an API key
  - Create .env file in the root directory of the project
  - Add the API key to the .env file as follows:

- To install libraries required:

```bash
pip install -r requirements.txt
```

- To run the chatbot:

```bash
streamlit run app.py
```

