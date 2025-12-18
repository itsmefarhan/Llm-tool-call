import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai
from google.genai import types

# --- 1. Tool returns RAW DATA now ---
def get_current_time(timezone: str):
    """
    Returns the raw date and time for a given IANA timezone.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        # We return a dictionary/JSON-like string so the LLM has to "read" it
        return {
            "city_timezone": timezone,
            "current_time": now.strftime("%I:%M %p"), # e.g., 10:30 PM
            "current_date": now.strftime("%A, %B %d, %Y"), # e.g., Monday, Dec 18
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- STREAMLIT UI ---
st.set_page_config(page_title="Reliable Time Bot", page_icon="🕒")
st.title("🕒 Ultimate City Time Bot")


if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add GEMINI_API_KEY to Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("What time is it in Dubai?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We tell Gemini exactly how to format the timezone strings
        sys_instr = "You are a time assistant. Use the get_current_time tool. Always provide the full IANA timezone (e.g., Asia/Dubai, Europe/Paris, America/New_York)."
        
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                tools=[get_current_time],
                system_instruction=sys_instr
            )
        )
        
        try:
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Chat Error: {e}")
