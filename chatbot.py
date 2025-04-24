import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

# Configure Gemini AI
genai.configure(api_key=api_key)

# Define system prompt for controlled AI responses
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

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)
if not st.experimental_user.is_logged_in:
    login_screen()
else:
    st.header(f"Welcome, {st.experimental_user.name}!")
st.button("Log out", on_click=st.logout)



# Initialize Gemini model with system instruction
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_PROMPT)

# Ensure chat session is stored
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
