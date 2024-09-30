import json
import os
import random
import string
import time

import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from streamlit.components.v1 import html

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", generation_config=generation_config
)

translations = {
    "en": {
        "title": "Your AI Mining Assistant",
        "tts_on": "📢 ON",
        "tts_off": "📢 OFF",
        "tts_tooltip": "Toggle Text-to-Speech",
        "chat_placeholder": "Ask away!",
        "thinking": "Thinking 🤔...",
        "transcribing": "Transcribing...",
        "generating_audio": "Generating audio response...",
        "speak_again": "Please speak again.",
        "user_first": "Hey!",
        "assistant_first": "Hi! How may I assist you today?",
    },
    "hi": {
        "title": "आपका AI खनन सहायक",
        "tts_on": "📢 चालू",
        "tts_off": "📢 बंद",
        "tts_tooltip": "टेक्स्ट-टू-स्पीच टॉगल करें",
        "chat_placeholder": "पूछिए!",
        "thinking": "सोच रहा हूँ 🤔...",
        "transcribing": "ट्रांसक्राइब कर रहा हूँ...",
        "generating_audio": "ऑडियो प्रतिक्रिया उत्पन्न कर रहा हूँ...",
        "speak_again": "कृपया फिर से बोलें।",
        "user_first": "नमस्ते",
        "assistant_first": "नमस्ते! मैं आज आपकी किस तरह से मदद कर सकता हूँ?",
    },
    "mr": {
        "title": "आपला AI खाण सहाय्यक",
        "tts_on": "📢 चालू",
        "tts_off": "📢 बंद",
        "tts_tooltip": "टेक्स्ट-टू-स्पीच टॉगल करा",
        "chat_placeholder": "विचारा!",
        "thinking": "विचार करत आहे 🤔...",
        "transcribing": "ट्रान्स्क्राइब करत आहे...",
        "generating_audio": "ऑडिओ प्रतिसाद तयार करत आहे...",
        "speak_again": "कृपया पुन्हा बोला.",
        "user_first": "नमस्कार",
        "assistant_first": "नमस्कार! मी आज तुमची कशी मदत करू शकतो?",
    },
}


def stream_data(data):
    speed = 0.0005
    if len(data) <= 100:
        speed = 0.05
    for char in data:
        yield char
        time.sleep(speed)


def speech_to_text(audio_data):
    try:
        audio_file = genai.upload_file(path=audio_data)
        prompt = "Generate a transcript of the speech. Format your response in JSON, including fields for 'transcript'."
        response = model.generate_content([prompt, audio_file]).text
        genai.delete_file(audio_file.name)
        res = json.loads(response)
        return res["transcript"]
    except Exception as e:
        print(e)
        return "error"


def image_detection(image_file):
    try:
        image_file = genai.upload_file(path=image_file)
        prompt = "You are an AI model specialized in detecting and analyzing environmental impact, safety concerns, and structural conditions in coal mining operations through image analysis. Your goal is to provide detailed assessments based on images of mining equipment, site conditions, and emissions-related visuals submitted by users. If the image is unclear, does not contain relevant mining elements, or is unsuitable for analysis, politely inform the user and request a clearer or more relevant image. Always prioritize safety and environmental concerns, offering suggestions to reduce emissions or improve site conditions when applicable. Format your response in JSON, including fields for 'area_of_concern', 'emission_level', and 'recommendations'."
        response = model.generate_content([prompt, image_file]).text
        genai.delete_file(image_file.name)
        res = json.loads(response)
        return res["area_of_concern"], res["emission_level"], res["recommendations"]
    except Exception as e:
        print(e)
        return "error"


def text_to_speech(input_text, lang_code, file_name):
    try:
        tts = gTTS(text=input_text, lang=lang_code, slow=False)

        tts.save(file_name)

        return file_name
    except Exception as e:
        print(e)
        return None


def get_answer(history, messages):
    system_message = "You are an ex coal mine executive and environmentalist with years of immense experience in coal mining and related activities. You have a good knowledge about different mining activities and various types of emissions. You are specialized in extracting different types of coal, reducing and tracking emissions. Use all this knowledge of yours to answer the following question. Ensure that all responses are relevant to mining and emissions, avoiding unrelated information. Format your response in JSON, including fields for 'response_text', 'language_code', and 'context_on_chat'."
    messages = (
        system_message + "; Previous talks: " + history + "; Prompt: " + messages + ";"
    )
    response = model.generate_content(messages).text
    res = json.loads(response)
    return res["response_text"], res["language_code"], res["context_on_chat"]


def gen_file_name(length, extension):
    letters_and_digits = string.ascii_letters + string.digits
    random_name = "".join(random.choice(letters_and_digits) for _ in range(length))
    file_name = f"{random_name}.{extension}"
    return file_name
