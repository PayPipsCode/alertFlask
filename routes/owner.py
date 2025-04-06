from flask import Blueprint, request, jsonify, current_app
from models.community_owner import CommunityOwner
from app import db
import uuid
import logging

owner_bp = Blueprint('owner_bp', __name__)

@owner_bp.route('/register', methods=['POST'])
def register_owner():
    logging.info("Received owner registration request")
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    community_name = data.get('community_name')
    terms = data.get('terms')  # expected boolean

    if not all([name, email, phone, community_name, terms]):
        logging.error("Missing required fields for owner registration")
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate unique token and signup link
    token = str(uuid.uuid4())
    base_url = current_app.config.get('BASE_URL').rstrip('/')
    unique_link = f"{base_url}/api/subscriber/signup?token={token}"
    
    owner = CommunityOwner(
        name=name,
        email=email,
        phone=phone,
        community_name=community_name,
        token=token,
        unique_link=unique_link
    )
    db.session.add(owner)
    db.session.commit()
    
    logging.info(f"Owner registered: {name}")
    return jsonify({
        'message': 'Registration successful',
        'unique_link': unique_link,
        'telegram_bot_username': owner.telegram_bot_username
    }), 200

@owner_bp.route('/dashboard', methods=['GET'])
def owner_dashboard():
    token = request.args.get('token')
    owner = CommunityOwner.query.filter_by(token=token).first()
    if not owner:
        return jsonify({'error': 'Invalid token'}), 400
    
    subscriber_count = len(owner.subscribers)
    # Dummy affiliate details for demo
    affiliate_earnings = 0  
    affiliate_info = {
        'subscriber_count': subscriber_count,
        'affiliate_earnings': affiliate_earnings,
        'unique_link': owner.unique_link
    }
    
    return jsonify(affiliate_info), 200
