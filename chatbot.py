import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

# Define system prompt for controlled AI responses
# SYSTEM_PROMPT = (
#     "You are an AI assistant that provides hints and guidance instead of direct code. "
#     "If a user asks for code, give conceptual guidance,hints , help him, or step-by-step instructions, "
#     "but do not provide the full solution directly."
#     "Your name is Sameer"
# )

# Initialize Gemini model with system instruction
model = genai.GenerativeModel("gemini-2.0-flash")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Function to clear chat history
def clear_chat():
    st.session_state.chat_session = model.start_chat(history=[])

# Streamlit UI
st.title("🔹 AI Chatbot with Gemini")
st.write("Ask me anything! I will guide you with **hints** instead of direct code.")

# Button to clear chat history
if st.button("🗑 Clear Chat History"):
    clear_chat()
    st.rerun()  # Refresh the page to reset chat history

# Display chat history
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
