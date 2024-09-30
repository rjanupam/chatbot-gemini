import concurrent.futures
import os

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from streamlit_option_menu import option_menu

from utils import (
    gen_file_name,
    get_answer,
    image_detection,
    speech_to_text,
    stream_data,
    text_to_speech,
    translations,
)

st.set_page_config(page_title="Mineo", page_icon="🤖")

# Initialize floating features for the interface
float_init()


def chatty(user_input):
    file_name = ""

    with st.chat_message("assistant"):
        with st.spinner(get_text("thinking")):
            response, code, history = get_answer(st.session_state.history, user_input)
        st.session_state.history += history

        if st.session_state.tts_enabled:
            file_name = gen_file_name(9, "mp3")

        st.session_state.messages.append(
            {"role": "assistant", "content": response, "audio_file": file_name}
        )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(text_to_speech, response, code, file_name)
            st.write_stream(stream_data(response))
            if st.session_state.tts_enabled:
                with st.spinner(get_text("generating_audio")):
                    audio_file = future.result()
                    if audio_file:
                        st.session_state.audio = False
                        st.rerun()


# Function to get translated text
def get_text(key):
    return translations[st.session_state.language][key]


def upload_set():
    st.session_state.upload = not st.session_state.upload


def toggle_audio():
    st.session_state.audio = not st.session_state.audio


# Initialize session state variables
if "language" not in st.session_state:
    st.session_state.language = "en"
if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True
if "history" not in st.session_state:
    st.session_state.history = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "upload" not in st.session_state:
    st.session_state.upload = False
if "image" not in st.session_state:
    st.session_state.image = 1
if "audio" not in st.session_state:
    st.session_state.audio = False

# Initialize messages if empty
if len(st.session_state.messages) == 0:
    if st.query_params:
        st.session_state.messages = [
            {"role": "user", "content": st.query_params.query, "audio_file": ""},
        ]
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        chatty(st.query_params.query)
    else:
        st.session_state.messages = [
            {"role": "user", "content": get_text("user_first"), "audio_file": ""},
            {
                "role": "assistant",
                "content": get_text("assistant_first"),
                "audio_file": "",
            },
        ]

# Language selector
selected_language = option_menu(
    menu_title=None,
    options=["Eng", "हिंदी", "मराठी"],
    default_index=["en", "hi", "mr"].index(st.session_state.language),
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#262730"},
        "icon": {"color": "orange"},
        "nav-link": {
            "color": "white",
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#0E2020",
        },
        "nav-link-selected": {"background-color": "#0E1110"},
    },
)

# Change language
language_map = {"Eng": "en", "हिंदी": "hi", "मराठी": "mr"}
if language_map[selected_language] != st.session_state.language:
    st.session_state.language = language_map[selected_language]
    if len(st.session_state.messages) == 2:
        st.session_state.messages = []
    st.rerun()

st.markdown(
    f"<h1 style='text-align: center;'>{get_text('title')}</h1>", unsafe_allow_html=True
)

# Main content
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["audio_file"] and os.path.exists(message["audio_file"]):
            with open(message["audio_file"], "rb") as f:
                data = f.read()
            player, download = st.columns(2)
            with player:
                st.audio(message["audio_file"])
            with download:
                st.download_button("📥", data, message["audio_file"])

# Footer
footer_container = st.container()
with footer_container:
    upload_box, prompt_box, mic_box = st.columns([0.1, 0.9, 0.1])
    with upload_box:
        upload_button = st.button("📤", on_click=upload_set)
    with prompt_box:
        prompt = st.chat_input(get_text("chat_placeholder"))
    with mic_box:
        mic_button = st.button("🎤", on_click=toggle_audio)

footer_container.float("background: #0E1117; bottom: 0rem; padding: 5px")

# Handle user input
if st.session_state.audio or prompt or st.session_state.upload:
    if st.session_state.audio:
        if st.session_state.audio:
            audio_bytes = audio_recorder(
                text="Click to Record",
                recording_color="#990000",
                neutral_color="#6aa36f",
                icon_name="microphone",
                icon_size="3x",
            )
        else:
            audio_bytes = None

        if audio_bytes:
            with st.spinner(get_text("transcribing")):
                webm_file_path = "temp_audio.mp3"
                with open(webm_file_path, "wb") as f:
                    f.write(audio_bytes)
                transcript = speech_to_text(webm_file_path)

            if transcript:
                st.session_state.messages.append(
                    {"role": "user", "content": transcript, "audio_file": ""}
                )
                with st.chat_message("user"):
                    st.write(transcript)
                chatty(transcript)
            else:
                st.error(get_text("speak_again"))

            os.remove(webm_file_path)
            st.session_state.audio = False

    elif prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "audio_file": ""}
        )
        with st.chat_message("user"):
            st.write(prompt)
        chatty(prompt)

    elif st.session_state.upload:
        image = st.file_uploader(
            "Choose an image", type=["jpg", "jpeg", "png"], key=st.session_state.image
        )
        if image:
            file_path = image.name
            image_bytes = image.getvalue()
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            st.session_state.messages.append(
                {"role": "user", "content": "Image detect.", "audio_file": ""}
            )
            with st.chat_message("user"):
                st.write("Image detect.")

            concern, emission, recommend = image_detection(file_path)
            response = f"{concern} | {emission} | {recommend}"
            st.session_state.messages.append(
                {"role": "assistant", "content": response, "audio_file": ""}
            )
            with st.chat_message("assistant"):
                st.write(response)

            os.remove(file_path)
            st.session_state.image += 1

# Custom CSS
st.markdown(
    """
    <style>
        .reportview-container {margin-top: -2em;}
        .stDeployButton {visibility: hidden;display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        body {background: #0E1117}
    </style>
    """,
    unsafe_allow_html=True,
)
