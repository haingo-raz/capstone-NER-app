import streamlit as st
import openai
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set up OpenAI API
openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key

# Questions list
questions = [
    "Please enter your desired food recommendation type.",
    "What type of food do you prefer in general?",
    "What do you want for breakfast?",
    "What do you want for lunch?",
    "What do you want for dinner?"
]

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'followup' not in st.session_state:
    st.session_state.followup = False

# Function to extract food preferences using spaCy
def extract_food_preferences(text):
    doc = nlp(text)
    preferences = {'breakfast': '', 'lunch': '', 'dinner': ''}
    for ent in doc.ents:
        if ent.label_ == "FOOD":  # Assuming FOOD entity label
            if 'breakfast' in ent.sent.text.lower():
                preferences['breakfast'] = ent.text
            elif 'lunch' in ent.sent.text.lower():
                preferences['lunch'] = ent.text
            elif 'dinner' in ent.sent.text.lower():
                preferences['dinner'] = ent.text
    return preferences

# Function to process input and move to next question
def process_input():
    current_question = questions[st.session_state.index]
    user_input = st.text_input("You:", key=f"input_{st.session_state.index}")
    
    if user_input:
        st.session_state.answers[current_question] = user_input
        
        # Handle dynamic skipping of questions based on extracted preferences
        if st.session_state.index == 0 and not st.session_state.followup:
            preferences = extract_food_preferences(user_input)
            if preferences['breakfast']:
                st.session_state.answers["What do you want for breakfast?"] = preferences['breakfast']
            if preferences['lunch']:
                st.session_state.answers["What do you want for lunch?"] = preferences['lunch']
            if preferences['dinner']:
                st.session_state.answers["What do you want for dinner?"] = preferences['dinner']
            st.session_state.followup = True
            st.session_state.index = 4  # Skip to the last question directly
        
        st.session_state.index += 1
        st.experimental_rerun()  # Rerun the app to update the question

st.title("Meal Planning Chatbot")

if st.session_state.index < len(questions):
    current_question = questions[st.session_state.index]
    
    if current_question in st.session_state.answers:
        st.session_state.index += 1
        st.experimental_rerun()
    else:
        st.write(f"Bot: {current_question}")
        process_input()
else:
    st.write("Bot: Thank you for sharing your preferences!")
    
  
    st.write("Here are your responses:")
    for question, answer in st.session_state.answers.items():
        st.write(f"- {question}: {answer}")
    
    
    prompt = "\n".join([f"{question}: {answer}" for question, answer in st.session_state.answers.items()])
    
    response = openai.Completion.create(
        engine="GPT-3.5",  
        prompt=prompt,
        max_tokens=150,
        stop=["\n", "You:", "Bot:"]
    )
    
    st.write("Bot:", response.choices[0].text.strip())
