import streamlit as st
import openai
from openai import OpenAI
from streamlit_chat import message

# Set your OpenAI API key
openai.api_key = "sk-proj-h9EdCxTdm625EJbKGFAxT3BlbkFJSWK3jfmGcbqDX2CZDxtR"

# Define the predefined questions at the top of the script
predefined_questions = [
    "How would you describe your eating style?🍽️ (example: Omnivore, Pescatarian, Vegetarian, Vegan, No restrictions, Other)",
    "Do you have any other dietary needs?🍽️ (Example: Dairy-Free🧀🚫, Gluten-Free🌾🚫, Soy-Free🌱🚫, Tree Nut-Free🌰🚫, Peanut-Free🥜🚫, Egg-Free🥚🚫, Shellfish-Free🦐🚫)",
    "Do you have any other food restrictions or allergies that I might have missed?📝(Example: No restrictions, nuts)",
    "What kinds of plant-based proteins do you like? (Beans + Lentils, Tofu + Tempeh, None of them, I like them all)",
    "Are there any foods you don't eat or don't like?🍅🥔 (For example: tomatoes, eggplants, mushrooms, cilantro, bell pepper, potato, garlic, onions, or anything else?)",
]

# Function used to get the response from the OpenAI API
def get_openai_response(prompt):
    system = [{"role": "system", "content": "You are a meal planning assistant."}]
    chat_history = st.session_state.messages
    user = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        messages=system + chat_history + user,
        model="gpt-3.5-turbo",
        max_tokens=150,
        top_p=0.9,
    )
    return response.choices[0].message["content"].strip()

# Function to generate the next question based on user profile and previous responses
def generate_next_question(profile, responses):
    profile_prompt = f"User profile: {profile}\n\n"
    questions_prompt = "Ask any from this list in order, 1 by 1, only if the key does not have a value yet:\n"
    
    for question in predefined_questions:
        if question not in responses:
            questions_prompt += f"- {question}\n"
    
    prompt = profile_prompt + questions_prompt
    return get_openai_response(prompt)

# Function to handle input change
def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.responses.append(user_input)
    st.session_state.user_input = ""  # Clear input after handling

# Function to handle button click
def on_btn_click():
    del st.session_state['questions']
    del st.session_state['responses']

st.session_state.setdefault('questions', [])
st.session_state.setdefault('responses', [])
st.session_state.setdefault('user_input', "")

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

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.responses = {}
    st.session_state.messages = []

# Sequentially ask each question from the list
while st.session_state.current_question < len(predefined_questions):
    question = predefined_questions[st.session_state.current_question]
    if question not in st.session_state.responses:
        next_question = generate_next_question(user_profile, st.session_state.responses)
        st.session_state.messages.append({"role": "assistant", "content": next_question})
        break
    else:
        st.session_state.current_question += 1

# Handle user input for current question
if st.session_state.current_question < len(predefined_questions):
    response = st.text_input(predefined_questions[st.session_state.current_question])
    if response:
        st.session_state.responses[predefined_questions[st.session_state.current_question]] = response
        st.session_state.current_question += 1

# Display all questions and responses
for i in range(st.session_state.current_question):
    st.write(f"**{predefined_questions[i]}**")
    st.write(f"{st.session_state.responses.get(predefined_questions[i], '')}")

# Display final responses after all questions are answered
if st.session_state.current_question >= len(predefined_questions):
    st.write("Thank you for answering all the questions! Here are your responses:")
    st.json(st.session_state.responses)

# Text input for user to ask for more personalized meal plans or dietary advice
prompt = st.text_input("Ask for more personalized meal plans or dietary advice")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner('Wait for it...'):
        full_response = get_openai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.markdown(full_response)

# Display messages using streamlit_chat
for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))

st.text_input("User Response:", on_change=on_input_change, key="user_input")
