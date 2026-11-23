import os
from urllib.parse import quote
import streamlit as st
from groq import Groq
from bot import answer

LOGO = "logo.png"
logo_exists = os.path.exists(LOGO)
BOT_AVATAR = LOGO if logo_exists else "🍲"

st.set_page_config(page_title="Essien's Kitchen", page_icon=BOT_AVATAR)

if logo_exists:
    st.image(LOGO, width=110)
st.title("Essien's Kitchen - Order with Ada")
st.caption("Fresh Nigerian meals, delivered across Lagos")  # change this tagline

try:
    key = st.secrets["GROQ_API_KEY"]
except Exception:
    key = os.getenv("GROQ_API_KEY")

if not key:
    st.error("GROQ_API_KEY is not set.")
    st.stop()

try:
    WHATSAPP_NUMBER = st.secrets["WHATSAPP_NUMBER"]
except Exception:
    WHATSAPP_NUMBER = "234XXXXXXXXXX"

client = Groq(api_key=key)

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    avatar = BOT_AVATAR if m["role"] == "assistant" else None
    with st.chat_message(m["role"], avatar=avatar):
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
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(reply)

# WhatsApp button: appears once Ada has written an order summary
last_summary = None
for m in reversed(st.session_state.history):
    if m["role"] == "assistant" and "ORDER SUMMARY" in m["content"].upper():
        last_summary = m["content"]
        break

if last_summary and "X" not in WHATSAPP_NUMBER:
    text = "Hi, I'd like to place this order:\n\n" + last_summary.replace("**", "*")
    link = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + quote(text)
    st.link_button("Send this order on WhatsApp", link, type="primary")
