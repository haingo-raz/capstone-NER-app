import streamlit as st
import spacy

# Load our custom model
nlp_ner = spacy.load(r"C:\Users\Namitha\Desktop\capstone\NER\model-best")

# Add a sentence segmentation component to the SpaCy pipeline
nlp_ner.add_pipe('sentencizer')

# Initialize the variables that will hold the input after NER implementation
breakfast_ner = []
lunch_ner = []
dinner_ner = []
snacks_ner = []

### Frontend interface ###
# Title and Introduction
st.title("Foodeasy - Personalized Meal Planning Assistant")
st.markdown("""
Hey friend! 👋 Hope your day is as awesome as your favorite meal! We're here to make your mealtime even more fun and stress-free! 🍽️✨

Let's chat about your eating habits and preferences so we can create something perfect for you! Ready?
""")

# Number of people for meal plan
st.markdown("**Awesome! Let's go! 🥳**")
st.markdown("**How many people are we preparing the meal plan for? 👨🍳 Just you, or a whole group? 👥**")
meal_plan_for = st.radio("Select an option:", ["Just me", "A group"])

# Top health goals
st.markdown("**What are your top health goals with Foodeasy? 🍽️ Pick up to 3 that matter most to you:**")
health_goals = st.multiselect(
    "Select your top health goals (up to 3):",
    [
        "Lose weight 🏋️‍♂️", "Save money 💸", "Simplify cooking 👩🍳", "Save time ⏰",
        "Try new things 🌟", "Improve health 💪", "Grocery shop less 🛒", "Waste less food 🌱", "Other (let us know!) 📝"
    ],
    max_selections=3
)
if "Other (let us know!) 📝" in health_goals:
    other_goal = st.text_input("Please specify your other goal:")

# Overview of usual meals
st.markdown("**Can you give me a quick overview of what you usually eat for each meal?**")
breakfast = st.text_area("Breakfast: 🍳", key="breakfast")
lunch = st.text_area("Lunch: 🥪", key="lunch")
dinner = st.text_area("Dinner: 🍝", key="dinner")
snacks = st.text_area("Snacks: 🍏", key="snacks")

# Handle the food input to only return the food items based on the custom SpaCy NER model
def process_input(text):
    result = [] # The processed input is saved here
    doc = nlp_ner(text.lower())
    negation_words = ['not', 'no', 'but', 'dislike', 'hate']
    liked_items = []
    disliked_items = []

    # Split the text into sentences to handle negation more accurately
    for sent in doc.sents:
        negation = False
        for token in sent:
            # Check if the current token is a negation word
            if token.text in negation_words:
                negation = True
            # Check if the token is an entity and its label is FOOD
            if token.ent_type_ == 'FOOD':
                if negation:
                    disliked_items.append(token.text)
                else:
                    liked_items.append(token.text)
        # Reset negation for the next sentence
        negation = False

    # Filter out disliked items from liked items
    result = [item for item in liked_items if item not in disliked_items]

    return result

# Submit button and feedback
if st.button("Submit and Get Recommendations"):

    # Pre-process the text input before saving into the user profiles
    breakfast_food = process_input(breakfast)
    lunch_food = process_input(lunch)
    dinner_food = process_input(dinner)
    snacks_food = process_input(snacks)

    user_profile = {
        "meal_plan_for": meal_plan_for,
        "health_goals": health_goals,
        "breakfast": breakfast_food,
        "lunch": lunch_food,
        "dinner": dinner_food,
        "snacks": snacks_food,
    }

    st.write(user_profile)
