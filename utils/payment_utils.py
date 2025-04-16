# backend/utils/payment_utils.py
import hashlib
import hmac
import json
import logging
import uuid

import requests
from flask import current_app

from app import db
from config import Config
from models import Subscriber

WEBHOOK_BASE_URL = Config.BASE_URL


def create_payment(subscriber, amount, processor='kora'):
    processor = processor.lower()
    if processor == 'kora':
        return create_kora_payment(subscriber, amount)
    elif processor == "paystack":
        amount = amount * 100  # Paystack needs amount in Kobo
        return create_paystack_payment(subscriber, amount)
    else:
        raise ValueError("Processor must be kora or paystack")


def create_kora_payment(subscriber: Subscriber, amount):
    secret_key = current_app.config.get('KORA_SECRET_KEY')
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    reference = generate_payment_reference()
    data = {
        "amount": amount,
        "metadata": {
            "subscriber_id": subscriber.id
        },
        'notification_url': f"{WEBHOOK_BASE_URL}/api/korapay/webhook",
        "currency": 'NGN',
        "customer": {
            'email': subscriber.email
        },
        "reference": reference,
        "merchant_bears_cost": False,
        "redirect_url": Config.FRONTEND_REDIRECT_URL,
    }

    response = requests.post("https://api.korapay.com/merchant/api/v1/charges/initialize", json=data, headers=headers)
    res_data = response.json()

    subscriber.txn_id = reference
    db.session.add(subscriber)
    db.session.commit()

    if res_data.get("status"):
        return res_data["data"]["checkout_url"]
    else:
        raise Exception(f"Failed to initiate Kora payment: {res_data}")


def create_paystack_payment(subscriber, amount):
    secret_key = current_app.config.get('PAYSTACK_SECRET_KEY')
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    data = {
        "email": subscriber.email,
        "amount": amount,  # amount in kobo (if using NGN)
        "metadata": {
            "subscriber_id": subscriber.id
        },
        "callback_url": f"{current_app.config.get('BASE_URL')}/api/paystack/callback"
    }
    response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    res_data = response.json()
    if res_data.get("status"):
        return res_data["data"]["authorization_url"]
    else:
        raise Exception("Failed to initiate Paystack payment")


def verify_paystack_payment(reference):
    secret_key = current_app.config.get('PAYSTACK_SECRET_KEY')
    headers = {"Authorization": f"Bearer {secret_key}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    return response.json()


def verify_kora_payment(reference):
    secret_key = Config.KORA_SECRET_KEY
    headers = {"Authorization": f"Bearer {secret_key}"}
    url = f"https://api.korapay.com/merchant/api/v1/charges/{reference}"
    response = requests.get(url, headers=headers)
    return response.json()


def verify_korapay_webhook(request, payload):
    """Helper function to verify the signature."""
    sig_header = request.headers.get('X-KORAPAY-SIGNATURE', '')
    data_bytes = json.dumps(payload['data'], separators=(',', ':')).encode('utf-8')
    expected_signature = hmac.new(Config.KORA_SECRET_KEY.encode('utf-8'), data_bytes,
                                  digestmod=hashlib.sha256).hexdigest()
    return sig_header == expected_signature


def generate_payment_reference():
    return str(uuid.uuid4())
