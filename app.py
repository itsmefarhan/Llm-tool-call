import streamlit as st
import requests
from google import genai
from google.genai import types

# --- TOOL DEFINITION ---
def get_current_time(timezone: str):
    """
    Fetches the current time for a timezone. 
    Args:
        timezone: IANA string like 'Asia/Karachi' or 'Asia/Dubai'.
    """
    # We use a header to look like a real browser (prevents 403/429 errors)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Using a highly reliable backup API
    url = f"https://worldtimeapi.org/api/timezone/{timezone}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return f"The current time in {timezone} is {data['datetime']}"
        else:
            return f"API Error: {response.status_code}. Gemini tried to look up: {timezone}"
    except Exception as e:
        return f"Connection failed: {str(e)}"

# --- STREAMLIT UI ---
st.set_page_config(page_title="Reliable Time Bot")
st.title("🕒 Global Time Bot")

# API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Secrets!")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Sidebar for Debugging (Very helpful on mobile!)
with st.sidebar:
    st.header("Debug Info")
    test_city = st.text_input("Test API manually:", "Asia/Karachi")
    if st.button("Check API Status"):
        res = get_current_time(test_city)
        st.write(res)

# Gemini Setup
tools = [get_current_time]
# We give Gemini a very specific instruction to fix the 'Karachi vs Asia/Karachi' issue
sys_instruct = "You are a time assistant. You MUST provide the full IANA timezone string (e.g., 'Asia/Karachi' instead of 'Karachi') when calling the tool."

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What time is it in Karachi?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat = client.chats.create(
                model='gemini-2.5-flash', 
                config=types.GenerateContentConfig(tools=tools, system_instruction=sys_instruct)
            )
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Gemini Error: {str(e)}")
