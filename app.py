import streamlit as st
import spacy
from openai import OpenAI
import re
import os
from textblob import TextBlob
# from tinydb import TinyDB

# Initialize chat history
# db = TinyDB('chat_history.json')

# Initialize chat history from previous sessions
# chat_history = db.all()

# Set your OpenAI API key
client = OpenAI(api_key="sk-proj-h9EdCxTdm625EJbKGFAxT3BlbkFJSWK3jfmGcbqDX2CZDxtR")

# Load our custom model
nlp_ner = spacy.load("NER\model-best")

# Add the 'sentencizer' component to the pipeline
# Add a sentence segmentation component to the SpaCy pipeline
# Sentencizer uses punctuation to determine sentence boundaries
nlp_ner.add_pipe('sentencizer')

# Initialize the user profile skeleton
user_profile = {
    "health_goals": [],
    "breakfast": None,
    "breakfast_time": None,
    "name": "",
    "age": None,
    "disliked_foods": [], # Food items the user dislikes
    "liked_foods": [],
    # "allergies": [], # User allergies
}

# Predefined questions
predefined_questions = [
    'What are your top health goals with Foodeasy?\n1. Lose weight\n2. Save money\n3. Simplify cooking\n4. Save time ⏰\n5. Try new things 🌟\n6. Improve health 💪\n7. Grocery shop less 🛒\n8. Waste less food 🌱\n9. Other (let us know!) 📝', 
    'Do you usually have breakfast?', 
    'How much time do you spend making it?', # This question is only asked if the user usually have breakfast
    'What is your name?',
    'How old are you?',
    # 'Do you have any other dietary needs? 1. Dairy-Free\n2. Gluten-Free\n3. Soy-Free \n 4. Tree Nut-Free \n5. Peanut-Free \n 6. Egg-Free\n 7. Shellfish-Free 🍽️ \n 8. Other', # Comment 5: To be able to record the last responses
]

# Function to extract entities using spaCy
def extract_entities(text):
    doc = nlp_ner(text.lower())
    negation_words = ['not', 'no', 'but', 'dislike', 'hate']
    liked_items = []
    disliked_items = []
    # allergies = []
    names = []
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
            # elif token.ent_type_ == 'ALLERGY': # TBD
            #     allergies.append(token.text)
        elif ent.label_ == 'PERSON': # TBD
            names.append(ent.text)
    negation = False

    # return liked_items, disliked_items, allergies, names
    return liked_items, disliked_items, names

# Function used to save the extracted entities to the user profile
# def update_profile_with_entities(liked_items, disliked_items, allergies, names):
def update_profile_with_entities(liked_items, disliked_items, names):
    st.session_state.user_profile["liked_foods"].extend(liked_items) # Added the user profile json into session_state
    st.session_state.user_profile["disliked_foods"].extend(disliked_items)
    # user_profile["allergies"].extend(allergies)
    if names:
        st.session_state.user_profile["name"] = names[0]

# Function used to get the response from the OpenAI API
def get_openai_response(prompt):
    system = [{"role": "system", "content": "You are a meal planning assistant."}]
    chat_history = st.session_state.messages
    user = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        messages=system + chat_history + user,
        model="gpt-3.5-turbo",
        max_tokens=50,
        top_p=0.9,
    )
    return response.choices[0].message.content

# Generate the next question
def generate_next_question(profile):
    profile_prompt = f"User profile: {profile}\n\n"
    questions_prompt = "Ask any from this list in order, 1 by 1, only if the key does not have a value yet:\n"
    for question in predefined_questions:
        questions_prompt += f"- {question}\n"

    prompt = profile_prompt + questions_prompt
    return get_openai_response(prompt)

#
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

# Add validation rules / guardrails to the user inputs here

# Update the user profile with the response
def update_profile_with_response(question, response):
    if question == "What is your name?":
        st.session_state.user_profile["name"] = response
    elif question == "How old are you?":
        st.session_state.user_profile["age"] = response # not fully int
    elif question == "Do you usually have breakfast?":
        affirmative_responses = ["yes", "y", "yeah", "yup", "sure", "of course", "always", "every day", "every morning", "usually", "often", "sometimes", "occasionally", "rarely"]
        st.session_state.user_profile["breakfast"] = response.lower() in affirmative_responses
        if not user_profile["breakfast"]:
            st.session_state.user_profile["breakfast_time"] = None
            if "How much time do you spend making it?" in predefined_questions:
                st.session_state.predefined_questions.remove("How much time do you spend making it?")
    elif question == "How much time do you spend making breakfast?":
        st.session_state.user_profile["breakfast_time"] = response # not fully int
    elif "What are your top health goals with Foodeasy?" in question:
        st.session_state.user_profile["health_goals"] = parse_health_goals(response)

# Streamlit setup
# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")
col1, col2 = st.columns([2, 1])

# Called everytime the user send a new input
def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.responses.append(user_input)

    # Extract entities from the user input
    # liked_items, disliked_items, allergies, names = extract_entities(user_input)
    liked_items, disliked_items, names = extract_entities(user_input)
    # Update the user profile with the extracted entities
    # update_profile_with_entities(liked_items, disliked_items, allergies, names)
    update_profile_with_entities(liked_items, disliked_items, names)

    # Update profile with user response to the current question
    current_question = st.session_state.current_question

    update_profile_with_response(current_question, user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    # Save in a tinydb database the user input
    # db.insert({"role": "user", "content": user_input})

    # Generate the next question based on the current user profile
    next_question = generate_next_question(st.session_state.user_profile)
    st.session_state.messages.append({"role": "assistant", "content": next_question})

# Initialize the questions list
st.session_state.setdefault('questions', [])

# Initialize the messages list if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages=[]

if "user_profile" not in st.session_state:
    st.session_state.user_profile = user_profile

# # Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = predefined_questions

if "current_question" not in st.session_state:
    st.session_state.current_question = predefined_questions[0]

# Responses are saved here
if 'responses' not in st.session_state:
    st.session_state.questions.extend(predefined_questions) # ??
    st.session_state.responses = []

with col1:
    st.title("FoodEasy Assistant")
    st.markdown("""
    Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
    """)

    # Where the conversation is displayed
    with st.container(height=420):
        with st.chat_message("assistant"):
            statement = "Type something in the chatbox to get started."
            st.write(statement)

        # How to keep displaying chat messages from history on app rerun

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
       
    # The chat input component
    with st.container():
        prompt = st.chat_input("Type your response here...", on_submit=on_input_change, key="user_input")

# Demonstration purposes
with col2:
    with st.container():
        st.markdown("Gathered user information:")
        st.write(st.session_state.user_profile)
        with st.container(height=250):
            st.markdown("Your responses:")
            st.write(st.session_state.responses)
        with st.container(height=250):
            st.markdown("Questions:")
            st.write(st.session_state.questions)