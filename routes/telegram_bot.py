from flask import Blueprint, request, jsonify
from models.community_owner import CommunityOwner
from app import db
import uuid

telegram_bp = Blueprint('telegram_bot', __name__, url_prefix='/telegram')

@telegram_bp.route('/onboard', methods=['POST'])
def onboard():
    """
    Endpoint for community owner onboarding.
    Expects JSON with keys: telegram_id, name, channel_name.
    """
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    telegram_id = data.get('telegram_id')
    name = data.get('name')
    channel_name = data.get('channel_name')
    
    if not telegram_id or not name or not channel_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate a unique token and link for signup.
    token = str(uuid.uuid4())
    base_url = request.host_url.rstrip('/')
    unique_link = f"{base_url}/telegram/signup?token={token}"
    
    community_owner = CommunityOwner(
        telegram_id=telegram_id,
        name=name,
        channel_name=channel_name,
        token=token,
        unique_link=unique_link
    )
    db.session.add(community_owner)
    db.session.commit()
    
    return jsonify({'message': 'Onboarding successful', 'unique_link': unique_link}), 200

@telegram_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Endpoint for subscriber signup.
    GET: Returns instructions.
    POST: Expects JSON with: name, email, phone, token.
    """
    if request.method == 'GET':
        token = request.args.get('token')
        return jsonify({
            'message': 'Please POST your details: name, email, phone, and token',
            'token': token
        })
    else:
        data = request.json
        token = data.get('token')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        
        if not all([token, name, email, phone]):
            return jsonify({'error': 'Missing fields'}), 400
        
        # Find the community owner using the token.
        community_owner = CommunityOwner.query.filter_by(token=token).first()
        if not community_owner:
            return jsonify({'error': 'Invalid token'}), 400
        
        # Create the subscriber with pending payment status.
        from models.subscriber import Subscriber
        subscriber = Subscriber(
            name=name,
            email=email,
            phone_number=phone,
            community_owner_id=community_owner.id,
            payment_status='pending'
        )
        db.session.add(subscriber)
        db.session.commit()
        
        return jsonify({
            'message': 'Signup successful. Proceed to payment.',
            'subscriber_id': subscriber.id
        }), 200
