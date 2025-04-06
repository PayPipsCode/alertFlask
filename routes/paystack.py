from flask import Blueprint, request, jsonify
import logging
from app import db
from models.subscriber import Subscriber
from utils.payment_utils import verify_paystack_payment

paystack_bp = Blueprint('paystack_bp', __name__)

@paystack_bp.route('/callback', methods=['GET'])
def paystack_callback():
    # Paystack typically sends a 'reference' parameter in the callback URL
    reference = request.args.get('reference')
    if not reference:
        logging.error("No reference provided in Paystack callback")
        return jsonify({'error': 'No reference provided'}), 400

    try:
        # Verify the transaction with Paystack
        verification_result = verify_paystack_payment(reference)
        logging.info(f"Verification result: {verification_result}")
        
        # Check if the payment was successful
        if verification_result.get("status") and verification_result["data"]["status"] == "success":
            # Extract the subscriber_id from metadata (as we set in our payment initialization)
            subscriber_id = verification_result["data"]["metadata"].get("subscriber_id")
            if not subscriber_id:
                logging.error("No subscriber_id in transaction metadata")
                return jsonify({'error': 'No subscriber_id in transaction metadata'}), 400

            # Retrieve the subscriber and update payment_status
            subscriber = Subscriber.query.get(subscriber_id)
            if not subscriber:
                logging.error(f"No subscriber found with id {subscriber_id}")
                return jsonify({'error': 'Subscriber not found'}), 404

            subscriber.payment_status = 'confirmed'
            db.session.commit()

            logging.info(f"Payment confirmed for subscriber {subscriber_id}")
            return jsonify({'message': 'Payment confirmed'}), 200
        else:
            logging.error("Payment verification failed")
            return jsonify({'error': 'Payment verification failed'}), 400

    except Exception as e:
        logging.exception("Exception during payment verification")
        return jsonify({'error': 'An error occurred during payment verification'}), 500
