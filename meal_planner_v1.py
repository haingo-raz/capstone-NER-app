import streamlit as st
import json
import spacy
from openai import OpenAI
import os
import PyPDF2
from docx import Document

# Set your OpenAI API key
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.title("Welcome to FoodEasy - Personalized Meal Planning Assistant")

st.markdown("""
Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
Please provide the following details to get started.
""")

# User profile form
with st.form("user_profile_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=0.0, step=0.1)
    submitted = st.form_submit_button("Submit")

if submitted:
    user_profile = {
        "name": name,
        "age": age,
        "weight": weight,
        "height": height
    }
    st.write("Thank you! Here is your profile:")
    st.json(user_profile)

st.markdown("""
### How to get more personalized recommendations:
You can ask for specific meal plans or dietary advice based on your profile. Just type your request in the input box below.
""")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "json"])

def read_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.type == "application/json":
        return json.load(file)
    elif file.type == "text/plain":
        return file.read().decode("utf-8")

if uploaded_file:
    file_content = read_file(uploaded_file)
    
    if isinstance(file_content, dict):
        file_content["user_profile"] = user_profile
    else:
        file_content += "\n" + json.dumps(user_profile)
    
    st.session_state.messages.append({"role": "user", "content": str(file_content)})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        system = [{"role": "system", "content": "You are a meal planning assistant."}]
        chat_history = st.session_state.messages
        user = [{"role": "user", "content": str(file_content)}]

        response = client.chat_completions.create(
            messages=system + chat_history + user,
            model="gpt-3.5-turbo",
            max_tokens=150,
            top_p=0.9,
        )

        full_response = response.choices[0].message.content.strip()
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

prompt = st.chat_input("Ask for more personalized meal plans or dietary advice")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        system = [{"role": "system", "content": "You are a meal planning assistant."}]
        chat_history = st.session_state.messages
        user = [{"role": "user", "content": prompt}]

        response = client.chat_completions.create(
            messages=system + chat_history + user,
            model="gpt-3.5-turbo",
            max_tokens=150,
            top_p=0.9,
        )

        full_response = response.choices[0].message.content.strip()
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
