import re
import json
import streamlit as st
import spacy
from textblob import TextBlob

client= '@@'

# Load our custom model
nlp_ner = spacy.load("./NER/model-best")
nlp_ner.add_pipe('sentencizer')

# Initialize the user profile skeleton
user_profile = {
    "name": "",
    "age": None,
    "top_health_goals": [],
    "have_breakfast": None,
    "breakfast_preparation_time": None,
    "liked_foods": [],
    "disliked_foods": [],
    "eating_preferences": [],
    "dietary_needs": [],
}

# Predefined questions
predefined_questions = [
    'What is your name?',
    'How old are you?',
    'What are your top health goals with Foodeasy?\n1. Lose weight\n2. Save money\n3. Simplify cooking\n4. Save time ⏰\n5. Try new things 🌟\n6. Improve health 💪\n7. Grocery shop less 🛒\n8. Waste less food 🌱\n9. Other (let us know!) 📝', 
    'Do you usually have breakfast?', 
    'How much time do you spend making breakfast?', 
    'What are some of your favorite foods?',
    'Are there any foods you dislike or avoid?',
    'Do you follow any specific diet or have any eating preferences (e.g., vegetarian, vegan, keto)?',
    'Do you have any dietary needs or food restrictions (e.g., milk, peanuts, gluten)?',
]

# Initialize the session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_profile" not in st.session_state:  
    st.session_state.user_profile = user_profile
if "questions" not in st.session_state:
    st.session_state.questions = predefined_questions.copy()
if "current_question" not in st.session_state:
    st.session_state.current_question = st.session_state.questions.pop(0)
if 'responses' not in st.session_state:
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
        json.dump(data, f, indent=4)

# Function to extract entities using spaCy
def extract_entities(text):
    doc = nlp_ner(text.lower())
    liked_items = []
    disliked_items = []
    preferences = []
    special_needs = []
    for ent in doc.ents:
        if ent.label_ == 'FOOD':
            sentence = next((sent for sent in doc.sents if ent.text in sent.text), None)
            if sentence:
                blob = TextBlob(sentence.text)
                sentiment = blob.sentiment.polarity
                if sentiment < 0:
                    disliked_items.append(ent.text)
                else:
                    liked_items.append(ent.text)
        elif ent.label_ == 'PREFERENCE':
            preferences.append(ent.text)
        elif ent.label_ == 'SPECIALNEED':
            special_needs.append(ent.text)
    return liked_items, disliked_items, preferences, special_needs

# Function used to save the extracted entities to the user profile
def update_profile_with_entities(liked_items, disliked_items, preferences, dietary_needs):
    st.session_state.user_profile["liked_foods"].extend(liked_items)
    st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    st.session_state.user_profile["eating_preferences"].extend(preferences)
    st.session_state.user_profile["dietary_needs"].extend(dietary_needs)

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

# Function to validate age
def is_valid_age(age):
    return age.isdigit() and 0 <= int(age) <= 120

# Function to validate name
def is_valid_name(name):
    return bool(re.match(r'^[A-Za-z\s]+$', name))

# Handling user responses
def update_profile_with_response(question, response):
    if "name" in question.lower():
        if is_valid_name(response):
            st.session_state.user_profile["name"] = response
            return True
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please provide a valid name. Only letters and spaces are allowed."})
            return False
    elif "old" in question.lower() or "age" in question.lower():
        if is_valid_age(response):
            st.session_state.user_profile["age"] = int(response)
            return True
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please provide a valid age between 0 and 120."})
            return False
    elif "breakfast" in question.lower():
        st.session_state.user_profile["have_breakfast"] = response
        if response.lower() in ["none", "nothing", "no", "don't eat breakfast"]:
            st.session_state.user_profile["breakfast_preparation_time"] = None
        return True
    elif "time" in question.lower():
        st.session_state.user_profile["breakfast_preparation_time"] = response
        return True
    elif "health goals" in question.lower():
        st.session_state.user_profile["top_health_goals"].extend(parse_health_goals(response))
        return True
    elif "favorite foods" in question.lower() or "foods you like" in question.lower():
        liked_items, disliked_items, preferences, dietary_needs = extract_entities(response)
        update_profile_with_entities(liked_items, disliked_items, preferences, dietary_needs)
        return True
    elif "foods you dislike" in question.lower() or "foods you avoid" in question.lower():
        _, disliked_items, _, _ = extract_entities(response)
        st.session_state.user_profile["disliked_foods"].extend(disliked_items)
        return True
    elif "diet or eating preferences" in question.lower():
        _, _, preferences, _ = extract_entities(response)
        st.session_state.user_profile["eating_preferences"].extend(preferences)
        return True
    elif "food allergies or intolerances" in question.lower():
        _, _, _, special_needs = extract_entities(response)
        st.session_state.user_profile["dietary_needs"].extend(special_needs)
        return True
    return False

# Generate the next question
def generate_next_question():
    if st.session_state.questions:
        return st.session_state.questions.pop(0)
    return "Thank you! All questions have been answered."

# Called every time the user sends a new input
def on_input_change():
    user_input = st.session_state.input_text
    st.session_state.responses.append(user_input)
    current_question = st.session_state.current_question

    if not user_input.strip():
        st.session_state.messages.append({"role": "assistant", "content": f"Please provide a valid response. {current_question}"})
        return

    if update_profile_with_response(current_question, user_input):
        st.session_state.messages.append({"role": "user", "content": user_input})
        next_question = generate_next_question()
        st.session_state.messages.append({"role": "assistant", "content": next_question})
        st.session_state.current_question = next_question
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})

    save_data()

# Streamlit UI
st.title("Personalized Meal Recommendation Chatbot")

# Display initial question if the chat is empty
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.current_question})

for msg in st.session_state.messages:
    st.write(f"**{msg['role']}**: {msg['content']}")

st.text_input("Type your response here...", key="input_text", on_change=on_input_change)
