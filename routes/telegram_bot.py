# backend/routes/telegram_bot.py
from flask import Blueprint, request, jsonify, current_app
import logging
import requests
from config import Config
from utils.twilio_utils import initiate_twilio_call  # Ensure this is implemented
from models.community_owner import CommunityOwner
from models.subscriber import Subscriber
from app import db

telegram_bp = Blueprint('telegram_bp', __name__)

def send_telegram_message(chat_id, text):
    """
    Sends a message to a Telegram chat using the Bot API.
    """
    token = Config.TELEGRAM_BOT_TOKEN  # Must be defined in your config
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        logging.info("Sent message to chat_id %s: %s", chat_id, response.json())
    except Exception as e:
        logging.exception("Failed to send message via Telegram")

def trigger_alert(owner_token, signal_message):
    """
    Retrieves subscribers for the community owner and initiates alerts via Twilio.
    """
    owner = CommunityOwner.query.filter_by(token=owner_token).first()
    if not owner:
        logging.error("Invalid owner token for alert trigger")
        return

    # Retrieve all subscribers with confirmed payment for this owner
    subscribers = Subscriber.query.filter_by(
        community_owner_id=owner.id, payment_status='confirmed'
    ).all()
    
    for subscriber in subscribers:
        try:
            # Initiate a call or notification for each subscriber
            initiate_twilio_call(subscriber.phone_number, signal_message)
            logging.info("Alert call initiated for subscriber %s", subscriber.phone_number)
        except Exception as e:
            logging.exception("Failed to alert subscriber %s", subscriber.phone_number)

@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Handles incoming Telegram updates.
    """
    update = request.get_json()
    logging.info("Received Telegram update: %s", update)
    
    # Check if the update contains a message
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        text_lower = text.lower()  # For case-insensitive checks

        # /start command: send a welcome message
        if text_lower == "/start":
            send_telegram_message(chat_id, "Welcome to AlertBySyncgram! To link this group to your account, use /setgroup <owner_token>.\n"
                                            "Then, you can drop trading signals like 'buy', 'sell', 'tp', or 'sl'.")
        
        # /setgroup command: link the group with a community owner's token
        elif text_lower.startswith("/setgroup"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                send_telegram_message(chat_id, "Usage: /setgroup <owner_token>")
            else:
                owner_token = parts[1].strip()
                owner = CommunityOwner.query.filter_by(token=owner_token).first()
                if owner:
                    owner.group_chat_id = chat_id
                    db.session.commit()
                    send_telegram_message(chat_id, "This group has been successfully linked to your account!")
                else:
                    send_telegram_message(chat_id, "Invalid owner token.")
        
        # Check for trading keywords (buy, sell, tp, sl)
        elif any(keyword in text_lower for keyword in ["buy", "sell", "tp", "sl"]):
            # Look up the community owner using the group_chat_id
            owner = CommunityOwner.query.filter_by(group_chat_id=chat_id).first()
            if owner:
                logging.info("Detected alert keywords in group message: %s", text)
                trigger_alert(owner.token, text)
                send_telegram_message(chat_id, "Alert signal processed. Subscribers are being notified.")
            else:
                send_telegram_message(chat_id, "This group is not linked to any community owner account. Use /setgroup <owner_token> to link.")
        else:
            logging.info("Received non-command message: %s", text)
    
    # Always respond with 200 OK to avoid Telegram retries
    return jsonify({'ok': True}), 200
