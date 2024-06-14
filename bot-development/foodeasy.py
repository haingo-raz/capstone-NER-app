import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import streamlit as st
from telegram.ext import Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define command handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! This is a Streamlit-powered bot.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def run_bot(token: str) -> None:
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(filters.text & ~filters.command, echo))
    updater.start_polling()
    updater.idle()

# Streamlit application
def start_streamlit_app():
    st.title("Telegram Bot with Streamlit")
    token = st.text_input("6193831344:AAHAB2VF4n99nF_7KByneOtqpZoxjZU1a78", type="password")
    
    if st.button('Start Bot'):
        if token:
            st.write("Bot is running...")
            run_bot(token)
        else:
            st.write("Please enter a valid token.")

if __name__ == '__main__':
    start_streamlit_app()
