import streamlit as st
import requests
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    temperature = st.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.slider('max_length', min_value=32, max_value=128, value=120, step=8)

# Store LLM generated responses and emotions
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
if "emotions" not in st.session_state:
    st.session_state.emotions = []

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.emotions = []
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating response from the served model
def generate_response(prompt_input, conversation):
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        json={
            "version": "your-replicate-model-version",
            "input": {"prompt": prompt_input, "conversation": conversation},
        },
        headers={"Authorization": f"Token {replicate_api}"},
    )
    response_json = response.json()
    return response_json["output"]

# Function for detecting emotion from the served model
def detect_emotion(conversation):
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        json={
            "version": "your-replicate-model-version",
            "input": {"conversation": conversation},
        },
        headers={"Authorization": f"Token {replicate_api}"},
    )
    response_json = response.json()
    return response_json["emotion"]

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            conversation = [msg["content"] for msg in st.session_state.messages]
            response = generate_response(st.session_state.messages[-1]["content"], conversation)
            st.write(response)
            emotion = detect_emotion(conversation)
            st.write(f"Detected emotion: {emotion}")
            st.session_state.emotions.append(emotion)
    st.session_state.messages.append({"role": "assistant", "content": response})
