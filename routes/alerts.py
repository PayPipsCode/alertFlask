from flask import Blueprint, request, jsonify
from models.community_owner import CommunityOwner
from models.subscriber import Subscriber
from models.alert_log import AlertLog
from app import db
from utils.twilio_utils import initiate_twilio_call
import logging

alerts_bp = Blueprint('alerts_bp', __name__)

@alerts_bp.route('/trigger', methods=['POST'])
def trigger_alert():
    logging.info("Received alert trigger request")
    data = request.json
    token = data.get('token')
    message = data.get('message')
    
    if not token or not message:
        logging.error("Missing token or message for alert trigger")
        return jsonify({'error': 'Missing token or message'}), 400
    
    owner = CommunityOwner.query.filter_by(token=token).first()
    if not owner:
        logging.error("Invalid token for alert trigger")
        return jsonify({'error': 'Invalid token'}), 400
    
    alert_log = AlertLog(message=message, community_owner_id=owner.id)
    db.session.add(alert_log)
    db.session.commit()
    
    subscribers = Subscriber.query.filter_by(
        community_owner_id=owner.id,
        payment_status='confirmed'
    ).all()
    
    for subscriber in subscribers:
        logging.info(f"Initiating call for subscriber {subscriber.phone_number}")
        initiate_twilio_call(subscriber.phone_number, message)
    
    logging.info(f"Alert triggered for {len(subscribers)} subscribers.")
    return jsonify({'message': f'Alert triggered for {len(subscribers)} subscribers.'}), 200
