import streamlit as st
import json
from openai import OpenAI
import os
import spacy
import PyPDF2
import docx

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set your OpenAI API key
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.title("Welcome to FoodEasy - Personalized Meal Planning Assistant")

st.markdown("""
Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
Please provide the following details to get started.
""")

# Initialize session state for user profile
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# User profile form
with st.form("user_profile_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=0.0, step=0.1)
    submitted = st.form_submit_button("Submit")

if submitted:
    st.session_state.user_profile = {
        "name": name,
        "age": age,
        "weight": weight,
        "height": height
    }
    st.write("Thank you! Here is your profile:")
    st.json(st.session_state.user_profile)
    
    # Save the user profile to a JSON file
    with open("user_profile.json", "w") as f:
        json.dump(st.session_state.user_profile, f)

st.markdown("""
### How to get more personalized recommendations:
You can ask for specific meal plans or dietary advice based on your profile. Just type your request in the input box below.
""")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "json"])

def read_file(file):
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfFileReader(file)
        content = ""
        for page in range(pdf_reader.numPages):
            content += pdf_reader.getPage(page).extractText()
        return content
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        content = "\n".join([para.text for para in doc.paragraphs])
        return content
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/json":
        return json.load(file)
    else:
        return None

if uploaded_file:
    file_content = read_file(uploaded_file)
    
    # Combine user profile and file content
    combined_content = {
        "user_profile": st.session_state.user_profile,
        "file_content": file_content
    }
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Automatically generate meal plan using user profile and file content
    system_message = {"role": "system", "content": "You are a meal planning assistant."}
    user_message = {"role": "user", "content": f"Create a meal plan based on this combined content: {json.dumps(combined_content)}"}
    
    st.session_state.messages.append(system_message)
    st.session_state.messages.append(user_message)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        max_tokens=500,  # Adjust as needed
        top_p=0.9,
    )

    full_response = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.write("Generated Meal Plan:")
    st.write(full_response)

# Input box for new messages
prompt = st.chat_input("Ask for more personalized meal plans or dietary advice")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages + [{"role": "user", "content": prompt}],
            max_tokens=500,  # Adjust as needed
            top_p=0.9,
        )

        full_response = response.choices[0].message.content.strip()
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
