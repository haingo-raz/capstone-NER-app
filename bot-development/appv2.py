import streamlit as st
import json


st.title("Foodeasy - Personalized Meal Planning Assistant")

st.markdown("""
**Got your microbiome or food sensitivity test results? Awesome!**  
If you’d like, you can upload your food recommendations file here or type in your results for us!
""")

uploaded_file = st.file_uploader("Upload your food recommendations file", type=["txt", "pdf", "docx"])
results_input = st.text_area("Or type in your results here")

st.markdown("""
**Awesome! Let's go! 🥳**  
So the first question is:  
**How many people are we preparing the meal plan for? 👨‍🍳 Just you, or a whole group? 👥**
""")

meal_plan_for = st.radio("Select an option:", ["Just me", "A group"])


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


    
# The question that was here is the same as the previous one but asked in another format
st.markdown("""
**Can you give me a quick overview of what you usually eat for each meal?**  
Just a brief summary based on what you've had over the past few days would be awesome!
""")  
breakfast = st.text_area("Breakfast: 🍳", key="breakfast")
lunch = st.text_area("Lunch: 🥪", key="lunch")
dinner = st.text_area("Dinner: 🍝", key="dinner")
snacks = st.text_area("Snacks: 🍏", key="snacks")

if st.button("Submit"):
    answers = {
        "meal_plan_for": meal_plan_for,
        "health_goals": health_goals,
        "meal_history_overview": {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "snacks": snacks
        }
    }
    with open("user_profile.json", "w") as file:
        json.dump(answers, file)
    st.success("Form submitted successfully!")