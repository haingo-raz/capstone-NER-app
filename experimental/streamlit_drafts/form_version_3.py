import streamlit as st
import json
import openai

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key-here'

# Function to get food recommendations from GPT-3.5
def get_food_recommendations(user_profile, recommendation_type):
    prompt = f"Based on the following user profile, provide a {recommendation_type}.\n\nUser Profile: {json.dumps(user_profile, indent=2)}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
    )

    recommendations = [choice['message']['content'].strip() for choice in response.choices]
    return recommendations

# Title and Introduction
st.title("Foodeasy - Personalized Meal Planning Assistant")
st.markdown("""
Hey friend! 👋 Hope your day is as awesome as your favorite meal! We're here to make your mealtime even more fun and stress-free! 🍽️✨

Let's chat about your eating habits and preferences so we can create something perfect for you! Ready?
""")

# File upload or text input for food recommendations
st.markdown("**Got your microbiome or food sensitivity test results? Awesome!**")
uploaded_file = st.file_uploader("Upload your food recommendations file", type=["txt", "pdf", "docx"])
results_input = st.text_area("Or type in your results here")

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

# Additional dietary preferences
st.markdown("**How would you describe your eating style? 🍽️**")
eating_style = st.radio(
    "Select your eating style:",
    ["Omnivore", "Pescatarian", "Vegetarian", "Vegan", "No restrictions", "Other (please tell us more!)"]
)
if eating_style == "Other (please tell us more!)":
    other_eating_style = st.text_input("Please specify your eating style:")

st.markdown("**Do you have any other dietary needs? 🍽️ You can always update this later.**")
dietary_needs = st.multiselect(
    "Select any dietary needs:",
    ["Dairy-Free 🧀🚫", "Gluten-Free 🌾🚫", "Soy-Free 🌱🚫", "Tree Nut-Free 🌰🚫", "Peanut-Free 🥜🚫", "Egg-Free 🥚🚫", "Shellfish-Free 🦐🚫"]
)

other_restrictions = st.text_area("Do you have any other food restrictions or allergies that I might have missed? 📝")

# Nutrition preferences
st.markdown("**Do you have any nutrition preferences? 🥗 Your choices help us suggest recipes that fit how you want to eat. Pick any that apply:**")
nutrition_preferences = st.multiselect(
    "Select your nutrition preferences:",
    ["Carb conscious (<35g) 🍞🚫", "High protein (>25g) 💪", "Gut friendly 🌿", "Less sodium (<480mg) 🧂🚫", "Anti-inflammatory 🌟", 
     "Immunity boosting 🛡️", "Less sugar (<2g added sugar) 🍬🚫", "Nothing specific 🤷‍♂️"]
)

# Meat preferences
st.markdown("**In what order do you like these types of meat? 🥩🍗 Just let us know your preferences!**")
meat_preferences = st.multiselect(
    "Select your preferred types of meat:",
    ["Beef + Bison (ex: meatballs, ground beef)", "Poultry (ex: grilled chicken, ground turkey)", "Pork (ex: carnitas, sliced ham)", 
     "Lamb (ex: lamb cubes, lamb chops)", "None of them 🚫", "Doesn’t matter, I like them all! 😋"]
)

# Seafood preferences
st.markdown("**What kinds of seafood do you like? 🐟🦐 Let us know your favorites in order!**")
seafood_preferences = st.multiselect(
    "Select your preferred types of seafood:",
    ["Fresh Fish (ex: cod, salmon)", "Smoked Fish (ex: lox, hot smoked salmon)", "Shellfish (ex: shrimp, crab, lobster)", 
     "Mollusks (ex: clams, oysters, mussels)", "Squid and Octopus", "None of them 🚫", "Doesn’t matter, I like them all! 😋"]
)

# Plant-based protein preferences
st.markdown("**What kinds of plant-based proteins do you like? 🌱🍲 Let us know your favorites in order!**")
plant_protein_preferences = st.multiselect(
    "Select your preferred plant-based proteins:",
    ["Tofu + Tempeh (ex: tofu nuggets, yuba noodles)", "Beans + Lentils (ex: simmered black beans, lentil dal)", 
     "‘Meat’ alternatives (ex: Beyond Meat, plant-based chorizo)", "None of them 🚫", "Doesn’t matter, I like them all! 😋"]
)

# Foods disliked or avoided
disliked_foods = st.text_area("Are there any foods you don't eat or don't like? 🍅🥔 (For example: tomatoes, eggplants, mushrooms, cilantro, bell pepper, potato, garlic, onions, or anything else?)")

# Meal and snack preferences
st.markdown("**What sounds good for breakfast? 🌞🍽️**")
breakfast_preferences = st.multiselect(
    "Select your breakfast preferences:",
    ["Sandwiches + wraps 🥪", "Smoothies 🍓", "Baked goods 🥐", "Cereal 🥣", "Coffee + tea ☕", "Oatmeal + granola 🍯", 
     "Yogurt 🥄", "Eggs 🍳", "Other"]
)

st.markdown("**What sounds good for lunch and dinner? 🌯🍔**")
lunch_dinner_preferences = st.multiselect(
    "Select your lunch and dinner preferences:",
    ["Sandwiches 🥪", "Bowls 🍲", "Wraps 🌯", "Main + Sides 🍛", "Stir-Fries 🍜", "Pastas 🍝", "Pizzas 🍕", "Salads 🥗", 
     "Burgers 🍔", "Tacos 🌮", "Other"]
)

st.markdown("**What snacks look good? 🍿🍏**")
snack_preferences = st.multiselect(
    "Select your snack preferences:",
    ["Chips, puffs + popcorn 🍿", "Juices 🥤", "Crackers + pretzels 🥨", "Dried fruit 🍇", "Snack packs 🎒", "Smoothies 🍓", 
     "Fresh fruit + veggies 🍎🥕", "Mini meals 🍱", "Cheese 🧀", "Bars + bites 🍫", "Jerky 🍖", "Pickles + olives 🥒🫒", 
     "Nuts, seeds + trail mix 🌰", "Other"]
)

# Cooking and meal preparation habits
st.markdown("**Let's talk about your meals and how much time you spend cooking or preparing them. ⏲️**")
breakfast_time = st.number_input("Do you usually have breakfast? 🍳 How much time do you spend making it? (minutes)", min_value=0, step=1)
lunch_time = st.number_input("Do you usually have lunch? 🥪 How much time do you spend making it? (minutes)", min_value=0, step=1)
dinner_time = st.number_input("Do you usually have dinner? 🍝 How much time do you spend making it? (minutes)", min_value=0, step=1)
snack_time = st.number_input("Do you usually have snacks? 🍏 How much time do you spend preparing them? (minutes)", min_value=0, step=1)

## Meal recommendation type selection
st.markdown("**Finally, what type of meal recommendation are you looking for? 🍽️**")
custom_recommendation_type = st.text_area("Type your custom recommendation type:", height=100)
if custom_recommendation_type.strip() == "":
    st.warning("Please enter a valid custom recommendation type.")
else:
    recommendation_type = custom_recommendation_type.strip()

# Generate recommendations based on user profile
if st.button("Get Recommendations"):
    user_profile = {
        "health_goals": health_goals,
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "snacks": snacks,
        "eating_style": eating_style,
        "dietary_needs": dietary_needs,
        "nutrition_preferences": nutrition_preferences,
        "meat_preferences": meat_preferences,
        "seafood_preferences": seafood_preferences,
        "plant_protein_preferences": plant_protein_preferences,
        "disliked_foods": disliked_foods,
        "breakfast_preferences": breakfast_preferences,
        "lunch_dinner_preferences": lunch_dinner_preferences,
        "snack_preferences": snack_preferences,
        "breakfast_time": breakfast_time,
        "lunch_time": lunch_time,
        "dinner_time": dinner_time,
        "snack_time": snack_time
    }

    recommendations = get_food_recommendations(user_profile, recommendation_type.lower())

    st.subheader(f"Here are your {recommendation_type.lower()} recommendations:")
    
    for index, recommendation in enumerate(recommendations):
        st.write(f"**Recommendation {index + 1}:** {recommendation}")
        st.write("Feedback:")
        st.button("👍", key=f"like_{index}")  
        st.button("👎", key=f"dislike_{index}")  
