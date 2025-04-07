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
    logging.debug("Sending message to chat_id %s: %s", chat_id, text)
    try:
        response = requests.post(url, json=payload)
        logging.info("Sent message to chat_id %s: %s", chat_id, response.json())
    except Exception as e:
        logging.exception("Failed to send message via Telegram to chat_id %s", chat_id)

def trigger_alert(owner_token, signal_message):
    """
    Retrieves subscribers for the community owner and initiates alerts via Twilio.
    Logs each step of the process.
    """
    logging.debug("Triggering alert for owner token: %s with message: %s", owner_token, signal_message)
    owner = CommunityOwner.query.filter_by(token=owner_token).first()
    if not owner:
        logging.error("Invalid owner token: %s", owner_token)
        return

    logging.debug("Found community owner: %s (ID: %s)", owner.name, owner.id)
    
    subscribers = Subscriber.query.filter_by(
        community_owner_id=owner.id, payment_status='confirmed'
    ).all()
    logging.debug("Found %d subscribers for owner %s", len(subscribers), owner.name)
    
    for subscriber in subscribers:
        logging.debug("Initiating alert for subscriber ID: %s, Phone: %s", subscriber.id, subscriber.phone_number)
        try:
            call_sid = initiate_twilio_call(subscriber.phone_number, signal_message)
            logging.info("Alert call initiated for subscriber %s, Call SID: %s", subscriber.phone_number, call_sid)
        except Exception as e:
            logging.exception("Failed to alert subscriber %s", subscriber.phone_number)

@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Handles incoming Telegram updates.
    Logs each step to help with debugging.
    """
    update = request.get_json()
    logging.info("Received Telegram update: %s", update)
    
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        text_lower = text.lower()
        logging.debug("Processing message from chat_id %s: %s", chat_id, text)
        
        # Handle /start command
        if text_lower == "/start":
            logging.info("Processing /start command for chat_id %s", chat_id)
            send_telegram_message(chat_id, "Welcome to AlertBySyncgram! To link this group to your account, use /setgroup <owner_token>.\nThen, you can drop trading signals like 'buy', 'sell', 'tp', or 'sl'.")
        
        # Handle /setgroup command: link group to community owner
        elif text_lower.startswith("/setgroup"):
            logging.info("Processing /setgroup command for chat_id %s", chat_id)
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                logging.warning("Owner token missing in /setgroup command for chat_id %s", chat_id)
                send_telegram_message(chat_id, "Usage: /setgroup <owner_token>")
            else:
                owner_token = parts[1].strip()
                logging.debug("Extracted owner token: %s from chat_id %s", owner_token, chat_id)
                owner = CommunityOwner.query.filter_by(token=owner_token).first()
                if owner:
                    logging.info("Linking group chat_id %s to owner %s", chat_id, owner.name)
                    owner.group_chat_id = chat_id
                    db.session.commit()
                    send_telegram_message(chat_id, "This group has been successfully linked to your account!")
                else:
                    logging.warning("Invalid owner token received: %s for chat_id %s", owner_token, chat_id)
                    send_telegram_message(chat_id, "Invalid owner token.")
        
        # Check for trading keywords ("buy", "sell", "tp", "sl")
        elif any(keyword in text_lower for keyword in ["buy", "sell", "tp", "sl"]):
            logging.info("Detected trading keywords in message from chat_id %s: %s", chat_id, text)
            # Look up the community owner using the group_chat_id
            owner = CommunityOwner.query.filter_by(group_chat_id=chat_id).first()
            if owner:
                logging.debug("Found owner %s for group chat_id %s", owner.name, chat_id)
                trigger_alert(owner.token, text)
                send_telegram_message(chat_id, "Alert signal processed. Subscribers are being notified.")
            else:
                logging.warning("No community owner linked to group chat_id %s", chat_id)
                send_telegram_message(chat_id, "This group is not linked to any community owner account. Use /setgroup <owner_token> to link.")
        else:
            logging.info("Received message without command or keywords: %s", text)
    
    else:
        logging.warning("Received update with no message field: %s", update)
    
    # Always return 200 OK to avoid Telegram retries.
    return jsonify({'ok': True}), 200
