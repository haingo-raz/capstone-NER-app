import streamlit as st

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 0

def next_step():
    st.session_state.step += 1

def reset_steps():
    st.session_state.step = 0

st.title("Foodeasy - Personalized Meal Planning Assistant")

if st.session_state.step == 0:
    st.markdown("""
    **Got your microbiome or food sensitivity test results? Awesome!**  
    If you’d like, you can upload your food recommendations file here or type in your results for us!
    """)
    uploaded_file = st.file_uploader("Upload your food recommendations file", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        next_step()
    else:
        results_input = st.text_area("Or type in your results here")
        if st.button("Next"):
            next_step()

elif st.session_state.step == 1:
    st.markdown("""
    **Awesome! Let's go! 🥳**  
    So the first question is:  
    **How many people are we preparing the meal plan for? 👨‍🍳 Just you, or a whole group? 👥**
    """)
    meal_plan_for = st.radio("Select an option:", ["Just me", "A group"])
    if st.button("Next"):
        next_step()

elif st.session_state.step == 2:
    st.markdown("""
    **What are your top health goals with Foodeasy? 🍽️ Pick up to 3 that matter most to you:**
    """)
    health_goals = st.multiselect(
        "Select your top health goals:",
        [
            "Lose weight 🏋️‍♂️", "Save money 💸", "Simplify cooking 👩‍🍳", "Save time ⏰",
            "Try new things 🌟", "Improve health 💪", "Grocery shop less 🛒", "Waste less food 🌱", "Other (let us know!) 📝"
        ]
    )
    if "Other (let us know!) 📝" in health_goals:
        other_goal = st.text_input("Please specify your other goal:")
    if st.button("Next"):
        next_step()

elif st.session_state.step == 3:
    st.markdown("""
    **Let's figure out your health goals with Foodeasy. I'll ask you a few quick questions to get a better idea of what you're looking for. Ready? Here we go!**
    """)
    
    lose_weight = st.radio("Are you looking to lose weight? 🏋️‍♂️", ["Yes", "No"])
    save_money = st.radio("How about saving money on your meals? 💸", ["Yes", "No"])
    simplify_cooking = st.radio("Would you like to simplify your cooking process? 👩‍🍳", ["Yes", "No"])
    save_time = st.radio("Do you want to save time when preparing meals? ⏰", ["Yes", "No"])
    try_new_things = st.radio("Are you interested in trying new foods and recipes? 🌟", ["Yes", "No"])
    improve_health = st.radio("Is improving your health a priority for you? 💪", ["Yes", "No"])
    reduce_shopping = st.radio("Would you like to reduce the amount of grocery shopping you do? 🛒", ["Yes", "No"])
    waste_less_food = st.radio("How important is it for you to waste less food? 🌱", ["Yes", "No"])
    other_goal_question = st.radio("Is there any other goal you have in mind that I didn't mention? 📝", ["Yes", "No"])
    if other_goal_question == "Yes":
        specific_goal = st.text_input("Please share your other goal:")
    
    if st.button("Next"):
        next_step()

elif st.session_state.step == 4:
    st.markdown("""
    **Can you give me a quick overview of what you usually eat for each meal?**  
    Just a brief summary based on what you've had over the past few days would be awesome!
    """)
    
    breakfast = st.text_area("Breakfast: 🍳")
    lunch = st.text_area("Lunch: 🥪")
    dinner = st.text_area("Dinner: 🍝")
    snacks = st.text_area("Snacks: 🍏")
    
    if st.button("Submit"):
        st.write("Thank you for providing the information! We're generating your personalized meal plan.")
        reset_steps()
        # Process the inputs and generate a meal plan (to be implemented)
