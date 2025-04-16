from datetime import datetime, timezone, timedelta

from flask import Blueprint, request, jsonify
import logging
from app import db
from models.subscriber import Subscriber
from utils.payment_utils import verify_kora_payment, verify_korapay_webhook
from utils.web import bad_request

kora_bp = Blueprint('kora_bp', __name__)


@kora_bp.route('/webhook', methods=['POST'])
def kora_callback():
    if 'X-KORAPAY-SIGNATURE' not in request.headers:
        return bad_request('Invalid request')

    payload = request.json
    signature_verified = verify_korapay_webhook(request, payload)

    if not signature_verified:
        return bad_request("Signature Mismatch")

    data = payload.get("data", {})
    reference = data.get("reference")

    try:
        verification_result = verify_kora_payment(reference)
        logging.info(f"Verification result: {verification_result}")

        # Check if the payment was successful
        if data.get("status") == "success" and verification_result["data"]["status"] == "success":
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
            today = datetime.now(tz=timezone.utc)
            subscriber.start_date = today
            subscriber.end_date = today + timedelta(days=30)
            db.session.commit()

            logging.info(f"Payment confirmed for subscriber {subscriber_id}")
            return jsonify({'message': 'Payment confirmed'}), 200
        else:
            logging.error("Payment verification failed")
            return jsonify({'error': 'Payment verification failed'}), 400

    except Exception:
        logging.exception("Exception during payment verification")
        return jsonify({'error': 'An error occurred during payment verification'}), 500
