import os
import streamlit as st
from groq import Groq
from bot import answer

st.set_page_config(page_title="Essien's Kitchen")
st.title("Essien's Kitchen - Order with Ada")

try:
    key = st.secrets["GROQ_API_KEY"]
except Exception:
    key = os.getenv("GROQ_API_KEY")

if not key:
    st.error("GROQ_API_KEY is not set.")
    st.stop()

client = Groq(api_key=key)

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("What would you like to order?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Ada is typing..."):
        reply, chunks = answer(st.session_state.history, prompt, client)
    reply = reply or "Sorry, something went wrong. Please try again."
    st.session_state.history += [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": reply},
    ]
    with st.chat_message("assistant"):
        st.markdown(reply)
