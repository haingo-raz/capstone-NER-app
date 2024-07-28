import streamlit as st
import spacy
from openai import OpenAI
import re
import json
import os
 
# Set your OpenAI API key from secrets
client = OpenAI(api_key=st.secrets["openai_apikey"])
 
# Load the SpaCy model
try:
    nlp_ner = spacy.load("../../NER/model-best")
except OSError as e:
    st.error(f"Error loading SpaCy model: {e}")
 
# Add the 'sentencizer' component to the pipeline
nlp_ner.add_pipe('sentencizer')
 
# Initialize the user profile skeleton
user_profile = {
    "name": "",
    "age": None,
    "health_goals": [],
    "breakfast": None,
    "breakfast_time": None,
    "disliked_foods": [],
    "liked_foods": [],
    "dietary_needs": [],
    "other_information": ""
}
 
# Reordered predefined questions
predefined_questions = [
    'Let\'s start! What do you want me to call you?',
    'How old are you?',
    'What are your top health goals with Foodeasy?\n1. Lose weight\n2. Save money\n3. Simplify cooking\n4. Save time ⏰\n5. Try new things 🌟\n6. Improve health 💪\n7. Grocery shop less 🛒\n8. Waste less food 🌱\n9. Other (let us know!) 📝',
    'What do you usually have for breakfast?',
    'How much time do you spend making it (breakfast)?',
    'What are some of your favorite foods?',
    'Are there any foods you dislike or avoid?',
    'Do you follow any specific diet or have any eating preferences (e.g., vegetarian, vegan, keto)?',
    'Do you have any food allergies or intolerances (e.g., gluten, dairy, nuts)?',
    'Please provide any other dietary needs or additional information you would like to share.',
    'Have you provided all the information you wanted to share? (yes or no)'
]
 
# Initialize the session state variables
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = [{"role": "assistant", "content": "Let's start! What do you want me to call you?"}]
    st.session_state.current_question = 0  # Use index to track current question
    st.session_state.user_profile = user_profile
    st.session_state.questions = predefined_questions
    st.session_state.responses = []
 
# Function to save user profile and chat history to a JSON file
def save_data():
    data = {
        "user_profile": st.session_state.user_profile,
        "messages": st.session_state.messages,
        "responses": st.session_state.responses,
        "current_question": st.session_state.current_question,
        "questions": st.session_state.questions
    }
    with open("chatbot_data.json", "w") as f:
        json.dump(data, f)
 
# Function to extract entities from the text
def extract_entities(text):
    doc = nlp_ner(text.lower())
    negation_words = ['not', 'no', 'but', 'dislike', 'hate', 'non', "don't", "won't", "isn't"]
    positive_words = ['love', 'like', 'want', 'enjoy', 'prefer', 'adore', 'crave', 'desire', 'fancy', 'wish', 'favor', 'cherish', 'appreciate']
    liked_items = []
    disliked_items = []
    preferences = []
    special_needs = []
    names = []
 
    for ent in doc.ents:
        if ent.label_ == 'FOOD':
            sentence = next(sent for sent in doc.sents if ent.text in sent.text)
            if any(neg_word in sentence.text for neg_word in negation_words):
                disliked_items.append(ent.text)
            elif any(pos_word in sentence.text for pos_word in positive_words):
                liked_items.append(ent.text)
        elif ent.label_ == 'PREFERENCE':
            preferences.append(ent.text)
        elif ent.label_ == 'SPECIALNEED':
            special_needs.append(ent.text)
        elif ent.label_ == 'PERSON':
            names.append(ent.text)
 
    return liked_items, disliked_items, preferences, special_needs, names
 
# Update the profile with the extracted entities
def update_profile_with_entities(liked_items, disliked_items, preferences, special_needs, names):
    st.session_state.user_profile["liked_foods"].extend(liked_items)
    st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    st.session_state.user_profile["dietary_needs"].extend(special_needs)
    st.session_state.user_profile["health_goals"].extend(preferences)
    if names:
        st.session_state.user_profile["name"] = names[0]
 
# Function to generate the next question
def generate_next_question(profile):
    st.session_state.current_question += 1
    if st.session_state.current_question < len(st.session_state.questions):
        return st.session_state.questions[st.session_state.current_question]
    else:
        return "Thank you! We have collected all the information we need."
 
# Function to parse health goals from the response
def parse_health_goals(response):
    goals_mapping = {
        "1": "Lose weight",
        "2": "Save money",
        "3": "Simplify cooking",
        "4": "Save time",
        "5": "Try new things",
        "6": "Improve health",
        "7": "Grocery shop less",
        "8": "Waste less food"
    }
   
    goals = []
    for key, value in goals_mapping.items():
        if re.search(rf'\b{key}\b', response) or re.search(value.lower(), response.lower()):
            goals.append(value)
    return goals
 
# Handling user responses
def update_profile_with_response(question, response):
    if "call you" in question.lower():
        st.session_state.user_profile["name"] = response
    elif "how old are you" in question.lower():
        try:
            st.session_state.user_profile["age"] = int(response)
        except ValueError:
            st.session_state.messages.append({"role": "assistant", "content": "I could not understand your reply. Can you please state your age in number-form (integer)?"})
            st.session_state.current_question -= 1
    elif "usually have for breakfast" in question.lower():
        st.session_state.user_profile["breakfast"] = response
        if response.lower() in ["none", "nothing", "no", "don't eat breakfast"]:
            st.session_state.user_profile["breakfast_time"] = None
            if "How much time do you spend making it (breakfast)?" in st.session_state.questions:
                st.session_state.questions.remove("How much time do you spend making it (breakfast)?")
    elif "health goals" in question.lower():
        st.session_state.user_profile["health_goals"].extend(parse_health_goals(response))
    elif "favorite foods" in question.lower() or "foods you like" in question.lower():
        liked_items, _, _, _, _ = extract_entities(response)
        st.session_state.user_profile["liked_foods"].extend(liked_items)
    elif "foods you dislike" in question.lower() or "foods you avoid" in question.lower():
        _, disliked_items, _, _, _ = extract_entities(response)
        st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    elif "diet or eating preferences" in question.lower():
        _, _, preferences, _, _ = extract_entities(response)
        st.session_state.user_profile["dietary_needs"].extend(preferences)
    elif "food allergies or intolerances" in question.lower():
        _, _, _, special_needs, _ = extract_entities(response)
        st.session_state.user_profile["dietary_needs"].extend(special_needs)
    elif "other dietary need" in question.lower() or "other information" in question.lower():
        st.session_state.user_profile["other_information"] = response
    elif "provided all the information" in question.lower():
        if response.lower() in ["yes", "y", "yeah", "yup", "sure", "of course"]:
            st.session_state.messages.append({"role": "assistant", "content": "Thank you! We have collected all the information we need."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please provide the remaining information."})
            st.session_state.current_question -= 1  # Ask the same question again
 
# Handling input change
def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.responses.append(user_input)
 
    current_question = st.session_state.questions[st.session_state.current_question]
 
    if "favorite foods" in current_question.lower() or "foods you dislike" in current_question.lower() or "diet or eating preferences" in current_question.lower() or "food allergies or intolerances" in current_question.lower():
        liked_items, disliked_items, preferences, special_needs, _ = extract_entities(user_input)
        update_profile_with_entities(liked_items, disliked_items, preferences, special_needs, [])
    else:
        update_profile_with_response(current_question, user_input)
 
    st.session_state.messages.append({"role": "user", "content": user_input})
 
    next_question = generate_next_question(st.session_state.user_profile)
    st.session_state.messages.append({"role": "assistant", "content": next_question})
 
    # Save data to JSON file
    save_data()
 
st.title("FoodEasy Assistant")
st.markdown("""
Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
""")
 
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
 
user_input = st.chat_input("Type your response here...", on_submit=on_input_change, key="user_input")
 
sidebar = st.sidebar
sidebar.markdown("## Gathered user information:")
sidebar.write(st.session_state.user_profile)
sidebar.markdown("## Current question:")
if st.session_state.current_question < len(st.session_state.questions):
    sidebar.markdown(st.session_state.questions[st.session_state.current_question])
else:
    sidebar.markdown("Thank you! We have collected all the information we need.")
sidebar.markdown("## Your responses:")
sidebar.write(st.session_state.responses)
sidebar.markdown("## Questions:")
sidebar.write(st.session_state.questions)