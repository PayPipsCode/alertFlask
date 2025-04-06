from flask import Blueprint, request, jsonify, current_app
from models.subscriber import Subscriber
from app import db
from utils.payment_utils import create_paystack_payment
import logging

paystack_bp = Blueprint('paystack_bp', __name__)

@paystack_bp.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    logging.info("Received payment initiation request")
    data = request.json
    subscriber_id = data.get('subscriber_id')
    if not subscriber_id:
        logging.error("Missing subscriber_id for payment")
        return jsonify({'error': 'Missing subscriber_id'}), 400
    
    subscriber = Subscriber.query.get(subscriber_id)
    if not subscriber:
        logging.error(f"Subscriber not found: {subscriber_id}")
        return jsonify({'error': 'Subscriber not found'}), 404
    
    # Set amount based on plan (amount in smallest currency unit)
    if subscriber.payment_plan == 'Basic':
        amount = 1899 * 100
    elif subscriber.payment_plan == 'Standard':
        amount = 2999 * 100
    else:
        return jsonify({'error': 'Invalid payment plan'}), 400
    
    try:
        payment_url = create_paystack_payment(subscriber, amount)
        logging.info(f"Payment initiated for subscriber {subscriber.id}")
    except Exception as e:
        logging.error(f"Error initiating payment: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'payment_url': payment_url}), 200

@paystack_bp.route('/webhook', methods=['POST'])
def paystack_webhook():
    logging.info("Received Paystack webhook event")
    data = request.json
    if data.get("event") == "charge.success":
        metadata = data["data"].get("metadata", {})
        subscriber_id = metadata.get("subscriber_id")
        if subscriber_id:
            from models.subscriber import Subscriber
            subscriber = Subscriber.query.get(subscriber_id)
            if subscriber:
                subscriber.payment_status = 'confirmed'
                db.session.commit()
                logging.info(f"Payment confirmed for subscriber {subscriber_id}")
    return '', 200
