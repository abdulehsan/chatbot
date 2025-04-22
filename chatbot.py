import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from oauthlib.oauth2 import WebApplicationClient
from urllib.parse import urlparse, parse_qs

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
api_key = os.getenv("API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

genai.configure(api_key=api_key)

# System Prompt for the chatbot
SYSTEM_PROMPT = """ 
You are a helpful AI assistant that guides users in solving coding problems.  
Instead of providing direct solutions, you give structured hints and insights  
that help them arrive at the solution on their own.  

### Instructions:  
- Provide **clear explanations** and **break problems down** into smaller parts.  
- You **can give pseudocode** or high-level logic but **not exact code**.  
- Ask **guiding questions** to help users think critically.  
- Offer **alternative approaches** where possible.  
- Ensure responses are **engaging, step-by-step, and easy to follow**.  

Your goal is to help users **learn and understand**, not just copy-paste solutions.
"""

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_PROMPT)

# Google OAuth 2.0 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Function to get the Google provider configuration
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Function to get the Google login URL with scope
def get_google_login_url():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Specify the required scopes (openid, email, and profile)
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://chatboo.streamlit.app",  # Replace with your Streamlit app's URI
        scope=["openid", "email", "profile"],  # Added the required scopes here
    )
    return request_uri

# Function to handle the OAuth callback and get user info
def get_google_user_info(token):
    google_provider_cfg = get_google_provider_cfg()
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    response = requests.get(userinfo_endpoint, headers={"Authorization": f"Bearer {token}"})
    return response.json()

# Function to authenticate the user and store token
def authenticate_user():
    if "google_token" in st.session_state:
        user_info = get_google_user_info(st.session_state["google_token"])
        st.session_state["google_user_info"] = user_info
        st.write(f"Logged in as {user_info['name']}")

    if "google_user_info" in st.session_state:
        st.write(f"Logged in as: {st.session_state['google_user_info']['name']}")

    if st.button("Login with Google"):
        google_login_url = get_google_login_url()
        st.write(f"[Click here to login with Google]({google_login_url})")

    # Check if we received the callback from Google
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        google_provider_cfg = get_google_provider_cfg()
        token_url = google_provider_cfg["token_endpoint"]
        token_response = requests.post(
            token_url,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": "https://chatboo.streamlit.app",  # Make sure this matches your redirect URI
                "grant_type": "authorization_code",
            },
        )
        token_json = token_response.json()
        st.session_state["google_token"] = token_json["access_token"]
        st.experimental_set_query_params()  # Clear the query parameters after the code exchange
        st.experimental_rerun()  # Reload the app after token exchange

# Function to start or clear chat history
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

def clear_chat():
    st.session_state.chat_session = model.start_chat(history=[])

# Title for the Streamlit app
st.title("🔹 AI Chatbot with Gemini")

# Authenticate user
authenticate_user()

# Button to clear chat history
if st.button("🗑 Clear Chat History"):
    clear_chat()
    st.rerun()  # Refresh the page to reset chat history

# Display chat history (chat messages)
for message in st.session_state.chat_session.history:
    with st.chat_message(message.role):
        st.markdown(message.parts[0].text)

# User input
user_input = st.chat_input("Enter your question...")

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    response = st.session_state.chat_session.send_message(user_input)

    # Display AI response with Markdown formatting
    with st.chat_message("assistant"):
        st.markdown(response.text)
