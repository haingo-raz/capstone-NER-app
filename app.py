import streamlit as st
import spacy
from openai import OpenAI
import re
from textblob import TextBlob
import json


# Set your OpenAI API key
client = OpenAI(api_key="sk-proj-h9EdCxTdm625EJbKGFAxT3BlbkFJSWK3jfmGcbqDX2CZDxtR")

# Load our custom model
nlp_ner = spacy.load("./NER/model-best")

# Add the 'sentencizer' component to the pipeline
# Sentencizer uses punctuation to determine sentence boundaries
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
    'How much time do you spend making breakfast?', # This question is only asked if the user usually have breakfast
    'What are some of your favorite foods?',
    'Are there any foods you dislike or avoid?',
    'Do you follow any specific diet or have any eating preferences (e.g., vegetarian, vegan, keto)?'
    'Do you have any dietary needs or food restrictions? (milk, peanuts, gluten, etc.)',
]

# Initialize the session state variables

# questions list
# st.session_state.setdefault('questions', [])

# Initialize the messages list if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages= [{"role": "assistant", "content": "Let's start! Type anything in the chatbox to begin."}]
if "user_profile" not in st.session_state:  
    st.session_state.user_profile = user_profile
# Questions that have been asked
if "questions" not in st.session_state:
    st.session_state.questions = predefined_questions
# The predefined questions
if "predefined_questions" not in st.session_state:
    st.session_state.predefined_questions = predefined_questions
if "current_question" not in st.session_state:
    st.session_state.current_question = "Let's start! Type anything in the chatbox to begin."
# User responses
if 'responses' not in st.session_state:
    st.session_state.questions.extend(predefined_questions) # ??
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

# Function to extract entities using spaCy
def extract_entities(text):
    doc = nlp_ner(text.lower())
    liked_items = []
    disliked_items = []
    preferences = []
    special_needs = []
    sentiments = 0
    for ent in doc.ents:
        if ent.label_ == 'FOOD':
            sentence = next(sent for sent in doc.sents if ent.text in sent.text)
            blob = TextBlob(sentence.text)
            sentiments= blob.sentiment.polarity
            print(sentiments)
            if sentiments < 0:
                disliked_items.append(ent.text)
            else:
                liked_items.append(ent.text)
        elif ent.label_ == 'PREFERENCE': # TBD
            preferences.append(ent.text)
        elif ent.label_ == 'SPECIALNEED': # TBD
            special_needs.append(ent.text)

    return liked_items, disliked_items, preferences, special_needs

# Function used to save the extracted entities to the user profile
# def update_profile_with_entities(liked_items, disliked_items, allergies, names):
def update_profile_with_entities(liked_items, disliked_items, preferences, dietary_needs):
    st.session_state.user_profile["liked_foods"].extend(liked_items) # Added the user profile json into session_state
    st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    st.session_state.user_profile["eating_preferences"].extend(preferences)
    st.session_state.user_profile["dietary_needs"].extend(dietary_needs)

# Function used to get the response from the OpenAI API
def get_openai_response(prompt):
    system = [{"role": "system", "content": "You are a customer onboarding assistant that asks ALL the predefined questions one by one. Wait for the user to answer one question before proceeding. Do not ask the same question more than once unless the key-value pair in the user profile corresponsing to the question is empty or irrelevant. When all predefined questions are answered, thank the user."}]
    chat_history = st.session_state.messages
    user = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        messages=system + chat_history + user,
        model="gpt-3.5-turbo",
        max_tokens=500,
        top_p=0.9,
    )
    return response.choices[0].message.content

# Generate the next question
def generate_next_question(profile):
    chat_history = st.session_state.messages
    profile_prompt = f"Our current user profile is: {profile}\n\n"
    questions_prompt = f"Based on the given user profile and the chat history {chat_history}, ask the listed questions in order 1 by 1 only if the matching property is still empty or irrelevant:\n"
    for question in st.session_state.predefined_questions:
        questions_prompt += f"- {question}\n"

    prompt = profile_prompt + questions_prompt
    return get_openai_response(prompt)
    # Comment: Add a condition to stop the Q and A here

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
    
    # Handle both numerical and textual responses
    goals = []
    for key, value in goals_mapping.items():
        if re.search(rf'\b{key}\b', response) or re.search(value.lower(), response.lower()):
            goals.append(value)
    return goals

# Handling user responses
def update_profile_with_response(question, response):
    if ("is your name?" or "I call you?" or "call you?") in question.lower():
        st.session_state.user_profile["name"] = response
    elif ("old are you?" or "is your age" or "What is your age?") in question:
        st.session_state.user_profile["age"] = response
        # try:
        #     st.session_state.user_profile["age"] = int(response)
        # except ValueError:
        #     st.session_state.messages.append({"role": "assistant", "content": "I could not understand your reply. Can you please state your age in number-form (integer)?"})
    elif ("usually have breakfast?" or "Do you eat breakfast?" or "Do you have breakfast?" or "Do you have breakfast in the morning?" or "Do you have breakfast every day?" or "Do you have breakfast every morning?" or "Do you have breakfast usually?" or "Do you have breakfast often?" or "Do you have breakfast sometimes?") in question.lower():
        st.session_state.user_profile["have_breakfast"] = response
        if response.lower() in ["none", "nothing", "no", "don't eat breakfast"]:
            st.session_state.user_profile["breakfast_preparation_time"] = None
            if "How much time do you spend making it (breakfast)?" in st.session_state.questions:
                st.session_state.questions.remove("How much time do you spend making it (breakfast)?")
    elif "How much time do you spend making breakfast?" in question.lower():
        st.session_state.user_profile["breakfast_preparation_time"] = response
    elif "health goals" in question:
        st.session_state.user_profile["top_health_goals"].extend(parse_health_goals(response))
    elif "favorite foods" in question.lower() or "foods you like" in question.lower():
        liked_items, _, _, _ = extract_entities(response)
        st.session_state.user_profile["liked_foods"].extend(liked_items)
    elif "foods you dislike" in question.lower() or "foods you avoid" in question.lower():
        _, disliked_items, _, _ = extract_entities(response)
        st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    elif "diet or eating preferences" in question.lower():
        _, _, preferences, _ = extract_entities(response)
        st.session_state.user_profile["preferences"].extend(preferences)
    elif "food allergies or intolerances" in question.lower():
        _, _, _, special_needs = extract_entities(response)
        st.session_state.user_profile["dietary_needs"].extend(special_needs)
    # Comment: end Q & A when all the questions are answered

# Streamlit setup
# st.set_page_config(layout="wide")
# col1, col2 = st.columns([2, 1])

# Called everytime the user send a new input
def on_input_change():
    # Get the latest user input
    user_input = st.session_state.user_input
    # Add the user input to the responses list
    st.session_state.responses.append(user_input)

    # Extract entities from the user input
    liked_items, disliked_items, preferences, dietary_needs = extract_entities(user_input)
    # Update the user profile with the extracted entities
    update_profile_with_entities(liked_items, disliked_items, preferences, dietary_needs)

    # Current question
    current_question = st.session_state.current_question

    # Get the current question and update the user profile based on that current question and provided input
    update_profile_with_response(current_question, user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate the next question based on the current user profile
    next_question = generate_next_question(st.session_state.user_profile)

    # Make the assistant ask the next question
    st.session_state.messages.append({"role": "assistant", "content": next_question})
    # The current question should be the last question asked by the assistant
    st.session_state.current_question = next_question

    # Save data to a JSON file
    save_data()



st.title("FoodEasy Assistant")
st.markdown("""
Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
Please provide the following details to get started.
""")

# Where the conversation is displayed
with st.container(height=420):
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
# The chat input component
with st.container():
    prompt = st.chat_input("Type your response here...", on_submit=on_input_change, key="user_input")

# Demonstration purposes in the sidebar
sidebar = st.sidebar
sidebar.markdown("Current question:")
sidebar.markdown(st.session_state.current_question)
sidebar.markdown("Your responses:")
sidebar.write(st.session_state.responses)
sidebar.markdown("Questions:")
sidebar.write(st.session_state.questions)
sidebar.markdown("Gathered user information:")
sidebar.write(st.session_state.user_profile)