from flask import Blueprint, request, jsonify
import logging
import requests
from config import Config  # Ensure your Config contains your bot token

telegram_bp = Blueprint('telegram_bp', __name__)

def send_telegram_message(chat_id, text):
    """
    Sends a message to a Telegram chat using the Bot API.
    """
    token = Config.TELEGRAM_BOT_TOKEN  # Make sure this is set in your config
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        logging.info("Sent message to chat_id %s: %s", chat_id, response.json())
    except Exception as e:
        logging.exception("Failed to send message via Telegram")

@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    logging.info("Received Telegram update: %s", update)
    
    # Check if this update contains a message with text
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Check for the /start command
        if text.strip() == "/start":
            send_telegram_message(chat_id, "Welcome to AlertBySyncgram! How can I help you today?")
        else:
            # Here you can add handling for other commands or messages
            logging.info("Received message: %s", text)
    
    # Always return a 200 OK so Telegram doesn't retry
    return jsonify({'ok': True}), 200
