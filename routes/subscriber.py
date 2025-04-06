# backend/routes/subscriber.py
from flask import Blueprint, request, jsonify, current_app
from models.subscriber import Subscriber
from models.community_owner import CommunityOwner
from app import db
import uuid
import logging
from utils.payment_utils import create_paystack_payment

subscriber_bp = Blueprint('subscriber_bp', __name__)

@subscriber_bp.route('/register', methods=['POST'])
def register_subscriber():
    logging.info("Received subscriber registration request")
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone')
    token = data.get('token')
    payment_plan = data.get('payment_plan')  # 'Basic' or 'Standard'
    terms = data.get('terms')  # boolean
    
    if not all([name, email, phone_number, token, payment_plan, terms]):
        logging.error("Missing required fields for subscriber registration")
        return jsonify({'error': 'Missing required fields'}), 400
    
    owner = CommunityOwner.query.filter_by(token=token).first()
    if not owner:
        logging.error("Invalid owner token provided")
        return jsonify({'error': 'Invalid token'}), 400
    
    subscriber = Subscriber(
        name=name,
        email=email,
        phone_number=phone_number,
        payment_plan=payment_plan,
        community_owner_id=owner.id,
        payment_status='pending'
    )
    db.session.add(subscriber)
    db.session.commit()
    
    # Determine the amount based on the selected payment plan.
    if payment_plan == "Basic":
        amount = 1899 * 100  # e.g., 1899 NGN in kobo
    elif payment_plan == "Standard":
        amount = 2999 * 100
    else:
        amount = 0
    
    try:
        payment_url = create_paystack_payment(subscriber, amount)
    except Exception as e:
        logging.exception("Failed to initialize payment")
        return jsonify({'error': 'Payment initialization failed'}), 500

    logging.info(f"Subscriber registered: {name}")
    return jsonify({
        'message': 'Registration successful. Proceed to payment.',
        'subscriber_id': subscriber.id,
        'payment_url': payment_url  # This URL will be used on the client side
    }), 200

@subscriber_bp.route('/signup', methods=['GET'])
def subscriber_signup_info():
    token = request.args.get('token')
    return jsonify({
        'message': 'Please POST your details: name, email, phone, token, payment_plan, terms'
    }), 200
