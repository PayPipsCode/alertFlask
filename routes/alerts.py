from datetime import datetime, timezone

from flask import Blueprint, request, jsonify

from config import Config
from models.community_owner import CommunityOwner
from models.subscriber import Subscriber
from models.alert_log import AlertLog
from app import db
from utils.twilio_utils import initiate_twilio_call, has_exceeded_daily_limit
import logging

from utils.web import bad_request

alerts_bp = Blueprint('alerts_bp', __name__)


@alerts_bp.route('/trigger', methods=['POST'])
def trigger_alert():
    logging.info("Received alert trigger request")
    data = request.json

    # Make sure it is coming from syncgram
    authorization = request.headers.get("Authorization")
    if authorization != Config.SYNC_GRAM_AUTH_TOKEN:
        return bad_request("Invalid authorization token", 403)

    message = data.get('message')
    group_chat_id = data.get('group_chat_id')

    if not group_chat_id or not message:
        logging.error("Missing group_chat_id or message for alert trigger")
        return bad_request("Missing token or message")
    
    owner = CommunityOwner.query.filter_by(group_chat_id=group_chat_id).first()
    if not owner:
        logging.error("Invalid token for alert trigger")
        return bad_request("Invalid token")
    
    alert_log = AlertLog(message=message, community_owner_id=owner.id)
    db.session.add(alert_log)
    db.session.commit()
    today = datetime.now(tz=timezone.utc)

    subscribers = Subscriber.query.filter(
        Subscriber.community_owner_id == owner.id,
        Subscriber.payment_status == 'confirmed',
        Subscriber.end_date >= today
    ).all()

    for subscriber in subscribers:
        logging.info(f"Initiating call for subscriber {subscriber.phone_number}")
        if not has_exceeded_daily_limit(subscriber.phone_number):
            initiate_twilio_call(subscriber.phone_number, message)
        else:
            logging.warning(f"Daily call limit exceeded for subscriber {subscriber.phone_number}")
    
    logging.info(f"Alert triggered for {len(subscribers)} subscribers.")
    return jsonify({'message': f'Alert triggered for {len(subscribers)} subscribers.'}), 200
