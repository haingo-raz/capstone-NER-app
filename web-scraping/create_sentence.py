import random

# Function to generate a random sentence
def generate_sentence(food):
    random_num = random.randint(1, 100)
    templates = [
        f"One of the most popular dishes in {random_num} countries is {food}.",
        f"Have you ever tried {food} with your {random_num} friends?",
        f"{food} is a delicious choice for any meal.",
        f"For a healthy option, consider adding {food} to your diet.",
        f"{food} can be used in a variety of recipes.",
        f"Many people enjoy eating {food} for breakfast.",
        f"Have you ever tasted {food}?",
        f"Consider adding {food} to your next meal.",
        f"Many people enjoy the taste of {food} at the Restaurant in {random_num} Forestview Drive Town.",
        f"{food} is a popular choice for many people.",
        f"Have you ever cooked with {food}?",
        f"Many people enjoy eating {food} for dinner.",
        f"{food} is a great option for a healthy snack.",
        f"There are more than {random_num} ways to cook {food}.",
        f"Where can you find {food} in your local area?",
        f"{food} can be used in a variety of dishes.",
        f"I usually eat {food} for lunch.",
        f"Most of the time, I eat {food} for breakfast.",
        f"The best way to cook {food} is to grill it.",
        f"Everything tastes better with a little bit of {food}.",
        f"Eating {food} is a great way to stay healthy.",
        f"I love the {food} from that restaurant.",
        f"In the morning, I like to eat {food}.",
    ]
    return random.choice(templates)

# Read the list of foods from the file
with open('food-list.txt', 'r', encoding='utf-8') as file:
    foods = [line.strip() for line in file.readlines()]

# Generate a sentence for each food and write to a new file
with open('more_food_data.txt', 'w', encoding='utf-8') as file:
    for food in foods:
        sentence = generate_sentence(food)
        file.write(sentence + "\n")

print('Random sentences have been written to more_food_data.txt')
