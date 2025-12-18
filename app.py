import streamlit as st
import requests
from google import genai
from google.genai import types

# 1. Define the Tool - NO API KEY REQUIRED HERE
def get_current_time(timezone: str):
    """
    Fetches the current date and time for a given IANA timezone.
    Args:
        timezone: The IANA timezone string (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo').
    """
    try:
        # Public API - No key needed
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Extracting date and time from the ISO string
            dt = data.get('datetime', 'Unknown')
            return f"The current date and time in {timezone} is {dt}."
        else:
            return f"Error: Could not find time for '{timezone}'. Please ensure it is a valid IANA timezone."
    except Exception as e:
        return f"Service error: {str(e)}"

# 2. Streamlit UI
st.set_page_config(page_title="No-Key Time Bot", page_icon="🕒")
st.title("🕒 Simple City Time Bot")
st.info("I use Gemini to map your city to a timezone and fetch live data with NO extra API keys.")

# Get Gemini Key from Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Tool config with explicit instructions for the LLM
tools = [get_current_time]
config = types.GenerateContentConfig(
    tools=tools,
    system_instruction="You are a helpful time assistant. When a user mentions a city, identify its IANA timezone (e.g., 'Europe/Paris' for Paris) and use the get_current_time tool to get the data."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's the time in Dubai?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat = client.chats.create(model='gemini-2.5-flash', config=config)
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
