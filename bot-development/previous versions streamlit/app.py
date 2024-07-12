import streamlit as st

st.title("Welcome to FoodEasy - Personalized Meal Planning Assistant")

st.markdown("""
Hello! Welcome to FoodEasy. We help you create personalized meal plans based on your profile.
Please provide the following details to get started.
""")

# Predefined list of questions
questions = [
    "How would you describe your eating style?🍽️ (example: Omnivore, Pescatarian, Vegetarian, Vegan, No restrictions, Other)",
    "Do you have any other dietary needs?🍽️ (Example: Dairy-Free🧀🚫, Gluten-Free🌾🚫, Soy-Free🌱🚫, Tree Nut-Free🌰🚫, Peanut-Free🥜🚫, Egg-Free🥚🚫, Shellfish-Free🦐🚫)",
    "Do you have any other food restrictions or allergies that I might have missed?📝(Example: No restrictions, nuts)",
    "What kinds of plant-based proteins do you like? (Beans + Lentils, Tofu + Tempeh, None of them, I like them all)",
    "Are there any foods you don't eat or don't like?🍅🥔 (For example: tomatoes, eggplants, mushrooms, cilantro, bell pepper, potato, garlic, onions, or anything else?)",
]

if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.responses = {}

if st.session_state.current_question < len(questions):
    question = questions[st.session_state.current_question]
    response = st.text_input(question)
    if response:
        st.session_state.responses[question] = response
        st.session_state.current_question += 1

    for i in range(st.session_state.current_question):
        st.write(f"**{questions[i]}**")
        st.write(f"{st.session_state.responses.get(questions[i], '')}")

else:
    st.write("Thank you for answering all the questions! Here are your responses:")
    st.json(st.session_state.responses)
