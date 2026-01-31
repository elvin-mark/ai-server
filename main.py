import streamlit as st
import requests
import json
import io

llm_url = "http://localhost:8181/v1/chat/completions"
tts_url = "http://localhost:8383/v1/audio/speech"
asr_url = "http://localhost:8080/inference"


def chatbot_response(prompt: str) -> str:
    res = requests.post(
        llm_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"messages": [{"role": "user", "content": prompt}]}),
    )
    return res.json()["choices"][0]["message"]["content"]


def text_to_speech(prompt: str) -> str:
    res = requests.post(
        tts_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "input": prompt,
                "temperature": 0.8,
                "top_k": 20,
                "repetition_penalty": 1.1,
                "response_format": "wav",
            }
        ),
    )
    return res.content


def automatic_speech_recognition(audio_file: io.BytesIO) -> str:
    res = requests.post(asr_url, files={"file": audio_file})
    return res.json()["text"]


msg = st.chat_input("Your message")
audio_file = st.audio_input("Send audio message")

if msg is None and audio_file:
    msg = automatic_speech_recognition(audio_file)

if msg:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append(("human", msg))
    llm_response = chatbot_response(msg)
    st.session_state.messages.append(("assistant", llm_response))

if "messages" in st.session_state:
    for agent, msg in st.session_state.messages:
        if agent == "human":
            human_msg = st.chat_message("human")
            human_msg.write(msg)
        elif agent == "assistant":
            assistant_msg = st.chat_message("assistant")
            assistant_msg.write(msg)
    _, last_message = st.session_state.messages[-1]
    audio_bytes = text_to_speech(last_message)
    st.audio(audio_bytes)
