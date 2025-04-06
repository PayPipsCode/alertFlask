import requests
from flask import current_app

def create_paystack_payment(subscriber, amount):
    secret_key = current_app.config.get('PAYSTACK_SECRET_KEY')
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    data = {
        "email": subscriber.email,
        "amount": amount,
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
