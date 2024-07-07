import telebot

# Define your token here
TELEGRAM_TOKEN = '7359229634:AAHAxQqkZc5dUI6zf2hF_Y9QMhURQplT54k'

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Remove webhook to avoid conflicts with polling
bot.remove_webhook()

# Define the URL to the welcome image
WELCOME_IMAGE_URL = 'https://as1.ftcdn.net/v2/jpg/03/76/07/04/1000_F_376070489_EzDpO7FxSlzytoetXp7e27fQCMzs6UgB.jpg'

# Define states for conversation
class States:
    START = 0
    WELCOME = 1

user_states = {}

def set_user_state(user_id, state):
    user_states[user_id] = state

def get_user_state(user_id):
    return user_states.get(user_id, States.START)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if get_user_state(message.chat.id) == States.START:
        bot.send_message(message.chat.id, "Hi! Welcome to FoodEasy.")
        bot.send_photo(message.chat.id, WELCOME_IMAGE_URL)
        set_user_state(message.chat.id, States.WELCOME)
    elif get_user_state(message.chat.id) == States.WELCOME:
        bot.send_message(message.chat.id, "How are you doing?")
        set_user_state(message.chat.id, States.START)

# Start polling with detailed logging
if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.debug("Starting bot polling")
    
    try:
        bot.polling()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
