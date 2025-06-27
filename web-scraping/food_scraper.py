# Scrap the food list on Wikipedia and write it to a file
import requests
from bs4 import BeautifulSoup

# Fetch the content from the URL
url = 'https://en.wikipedia.org/wiki/Lists_of_foods'
response = requests.get(url)
html = response.content

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

# Find the list items within the page
food_list_items = soup.find_all('li')

# Open a file to write
with open('list_of_foods.txt', 'w', encoding='utf-8') as file:
    for item in food_list_items:
        # Extract text from each list item
        text = item.get_text()
        # Write the food item to the file
        file.write(f"{text}\n")

print('List of foods has been written to list_of_foods.txt')
