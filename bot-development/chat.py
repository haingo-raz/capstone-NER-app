import streamlit as st
import openai
import sqlite3
import os
import json
import tempfile
from embedchain import App as ChatbotApp


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


DB_PATH = "chatbot.db"

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT
        )
    ''')
    conn.commit()
    return conn

def insert_config(conn, key, value):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def fetch_config(conn, key):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
    result = cursor.fetchone()
    return result[0] if result else None

def initialize_chatbot(db_path):
    conn = initialize_db(db_path)
    
    api_key = fetch_config(conn, "api_key")
    if not api_key:
        insert_config(conn, "api_key", OPENAI_API_KEY)
        api_key = OPENAI_API_KEY

    config = {
        "llm": {"provider": "openai", "config": {"api_key": api_key}},
        "embedder": {"provider": "openai", "config": {"api_key": api_key}}
    }
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w', encoding='utf-8') as temp_config_file:
        json.dump(config, temp_config_file)
        config_path = temp_config_file.name

    chatbot = ChatbotApp.from_config(config_path)
    
    os.remove(config_path)
    conn.close()
    
    return chatbot

def analyze_sentiment(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that performs sentiment analysis."},
                {"role": "user", "content": f"Analyze the sentiment of the following text and categorize each item as 'like' or 'dislike'. Return the result as a JSON object. Text: {text}"}
            ]
        )
        return json.loads(response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"Error in sentiment analysis: {e}")
        return {}

st.title("Foodeasy Personalized Meal Plan Chatbot")


try:
    chatbot = initialize_chatbot(DB_PATH)
except Exception as e:
    st.error(f"Failed to initialize the chatbot: {e}")
    st.stop()


if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {}
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 0


questions = [
    {
        "key": "health_goals",
        "question": "What are your top health goals with Foodeasy? Pick up to 3 that matter most to you:",
        "type": "multiselect",
        "options": ["Lose weight", "Save money", "Simplify cooking", "Save time", "Try new things", "Improve health",
                    "Grocery shop less", "Waste less food", "Other"]
    },
    {
        "key": "eating_style",
        "question": "How would you describe your eating style?",
        "type": "selectbox",
        "options": ["Omnivore", "Pescatarian", "Vegetarian", "Vegan", "No restrictions", "Other"]
    },
    {
        "key": "food_preferences",
        "question": "Tell us about your food preferences (e.g., 'I like banana and hate mango'):",
        "type": "text_input"
    },
    {
        "key": "desired_meal_plan",
        "question": "What is your desired meal plan? Please describe what you would like to eat.",
        "type": "text_area"
    }
]


if st.session_state['current_question'] < len(questions):
    current_q = questions[st.session_state['current_question']]
    st.subheader(f"Question {st.session_state['current_question'] + 1}")
    
    if current_q["type"] == "multiselect":
        response = st.multiselect(current_q["question"], options=current_q["options"])
    elif current_q["type"] == "selectbox":
        response = st.selectbox(current_q["question"], options=current_q["options"])
    elif current_q["type"] in ["text_input", "text_area"]:
        response = st.text_input(current_q["question"]) if current_q["type"] == "text_input" else st.text_area(current_q["question"])
    
    if st.button("Next"):
        if current_q["type"] in ["text_input", "text_area"]:
            sentiment_json = analyze_sentiment(response)
            st.session_state['user_profile'][current_q["key"]] = {
                "raw_input": response,
                "sentiment_analysis": sentiment_json
            }
        else:
            st.session_state['user_profile'][current_q["key"]] = response
        st.session_state['current_question'] += 1
        st.experimental_rerun()


elif st.session_state['current_question'] == len(questions):
    st.subheader("Generate Meal Plan")
    if st.button("Generate Meal Plan"):
        try:
            
            prompt = "Generate a personalized meal plan based on the following information:\n"
            for q in questions:
                if isinstance(st.session_state['user_profile'].get(q['key']), dict):
                    prompt += f"{q['question']} Raw input: {st.session_state['user_profile'][q['key']]['raw_input']}\n"
                    prompt += f"Sentiment analysis: {json.dumps(st.session_state['user_profile'][q['key']]['sentiment_analysis'])}\n"
                else:
                    prompt += f"{q['question']} {st.session_state['user_profile'].get(q['key'], 'Not specified')}\n"

            # Use the chatbot to generate meal recommendations
            meal_recommendations = chatbot.query(prompt)
            
            st.success(meal_recommendations)
            
            # Add chatbot's response to chat history
            st.session_state['chat_history'].append(f"Chatbot: {meal_recommendations}")
            
            # Move to the next state
            st.session_state['current_question'] += 1
        except Exception as e:
            st.error(f"Error generating meal plan: {e}")

# Display chat history and user profile
else:
    st.subheader("Chat History")
    for message in st.session_state['chat_history']:
        st.text_area("", value=message, height=100, max_chars=None, disabled=True)
    
    st.sidebar.header("User Profile")
    for key, value in st.session_state['user_profile'].items():
        if isinstance(value, dict):
            st.sidebar.text(f"{key}:")
            st.sidebar.json(value)
        else:
            st.sidebar.text(f"{key}: {value}")

    if st.button("Start Over"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()


def cleanup():
    conn = sqlite3.connect(DB_PATH)
    conn.close()

st.button("End Chat", on_click=cleanup)