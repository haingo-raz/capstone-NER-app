import streamlit as st
import openai
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

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.responses = {}
    st.session_state.messages = []
    st.session_state.user_profile = {}

# Function to handle input change
def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.responses[st.session_state.current_question] = user_input
    st.session_state.user_input = ""  # Clear input after handling
    st.session_state.current_question += 1

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
    st.session_state.user_profile = user_profile  # Store the user profile in session state
    st.write("Thank you! Here is your profile:")
    st.json(user_profile)

if 'user_profile' in st.session_state and st.session_state.user_profile:
    st.markdown("""
    ### How to get more personalized recommendations:
    Answer the following questions to help us understand your dietary preferences better.
    """)

    # Sequentially ask each question from the list
    if st.session_state.current_question < len(predefined_questions):
        question = predefined_questions[st.session_state.current_question]
        st.write(question)
        st.text_input("Your answer:", key="user_input", on_change=on_input_change)

    # Display all questions and responses
    for i in range(st.session_state.current_question):
        st.write(f"**{predefined_questions[i]}**")
        st.write(f"{st.session_state.responses.get(i, '')}")

    # Display final responses after all questions are answered
    if st.session_state.current_question >= len(predefined_questions):
        st.write("Thank you for answering all the questions! Here are your responses:")
        st.json(st.session_state.responses)
else:
    st.write("Please submit your profile to proceed.")
