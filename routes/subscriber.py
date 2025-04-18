# backend/routes/subscriber.py
import datetime

from flask import Blueprint, request, jsonify
from models.subscriber import Subscriber
from models.community_owner import CommunityOwner
from app import db
import logging
from utils.payment_utils import create_payment
from utils.web import bad_request

subscriber_bp = Blueprint('subscriber_bp', __name__)


@subscriber_bp.route('/register', methods=['POST'])
def register_subscriber():
    logging.info("Received subscriber registration request")
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone')
    token = data.get('token')
    
    if not all([name, email, phone_number, token]):
        logging.error("Missing required fields for subscriber registration")
        return jsonify({'error': 'Missing required fields'}), 400

    owner = CommunityOwner.query.filter_by(token=token).first()
    if not owner:
        logging.error("Invalid owner token provided")
        return bad_request("Invalid token")

    existing_subscriber = (
        db.session.query(Subscriber)
        .join(CommunityOwner)
        .filter(
            CommunityOwner.token == token,
            Subscriber.phone_number == phone_number,
            Subscriber.payment_status == 'confirmed'
        )
        .first()
    )

    if existing_subscriber:
        return bad_request("Phone number already registered for this community")

    subscriber = Subscriber(
        name=name,
        email=email,
        phone_number=phone_number,
        payment_plan="",
        community_owner_id=owner.id,
        payment_status='confirmed',
    )
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    subscriber.start_date = today
    subscriber.end_date = datetime.date(2025, 4, 26)

    db.session.add(subscriber)
    db.session.commit()

    # amount = 1000
    #
    # try:
    #     payment_url = create_payment(subscriber, amount)
    # except Exception as e:
    #     logging.exception("Failed to initialize payment")
    #     return bad_request("Payment initialization failed", 500)
    #
    # logging.info(f"Subscriber registered: {name}")
    # return jsonify({
    #     'message': 'Registration successful. Proceed to payment.',
    #     'subscriber_id': subscriber.id,
    #     'payment_url': payment_url  # This URL will be used on the client side
    # }), 200

    community_name = subscriber.owner.community_name
    return jsonify({"data": {"status": subscriber.payment_status, "name": subscriber.name,
                             "email": subscriber.email, "phone": subscriber.phone_number,
                             "community_name": community_name}})


@subscriber_bp.route('/payment-status', methods=['GET'])
def payment_status():
    reference = request.args.get('reference', None)

    if not reference:
        return bad_request("Missing reference parameter")

    subscriber = Subscriber.query.filter_by(txn_id=reference).first()
    if not subscriber:
        return bad_request("Subscription not found", 404)

    community_name = subscriber.owner.community_name
    return jsonify({"data": {"status": subscriber.payment_status, "name": subscriber.name,
                             "email": subscriber.email, "phone": subscriber.phone_number, "community_name": community_name }})


@subscriber_bp.route('/signup', methods=['GET'])
def subscriber_signup_info():
    token = request.args.get('token')
    return jsonify({
        'message': 'Please POST your details: name, email, phone, token, payment_plan, terms'
    }), 200
