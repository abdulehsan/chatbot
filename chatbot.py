import streamlit as st
import os
from dotenv import load_dotenv
from google import genai    
load_dotenv()

api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

st.title("Chatbot with Google Gemini")

prompt = st.text_input("Enter your question:")

# Ensure the prompt is not empty before sending request
if prompt.strip():
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[prompt]  # Ensure input is a list
    )

    # Stream response properly
    for chunk in response:
        st.write(chunk.text)
else:
    st.warning("Please enter a valid question before submitting.")