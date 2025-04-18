import logging
from twilio.rest import Client
from flask import current_app
from urllib.parse import quote_plus
from datetime import datetime, timezone, timedelta

from models.call_logs import CallLog

MAX_DAILY_CALL_LIMIT = 2


def initiate_twilio_call(phone_number, message):
    logging.debug("Initiating Twilio call to %s with message: %s", phone_number, message)
    account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = current_app.config.get('TWILIO_PHONE_NUMBER')
    
    client = Client(account_sid, auth_token)
    
    # URL encode the message, so it is safe to pass in a query string
    encoded_message = quote_plus(message)
    
    try:
        call = client.calls.create(
            to=phone_number,
            from_=twilio_phone_number,
            url=f"{current_app.config.get('BASE_URL')}/api/twilio/voice?msg={encoded_message}",
            status_callback=f"{current_app.config.get('BASE_URL')}/api/twilio/status_callback",
            status_callback_event=['completed']
        )
        logging.info("Twilio call initiated to %s, Call SID: %s", phone_number, call.sid)
        return call.sid
    except Exception as e:
        logging.exception("Failed to initiate Twilio call to %s", phone_number)
        raise


def has_exceeded_daily_limit(phone_number, max_calls=MAX_DAILY_CALL_LIMIT):
    # Get the start of today in UTC
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    # We need to query for calls matching the phone number made after start of day
    call_count = CallLog.query.filter(
        CallLog.phone_number == phone_number,
        CallLog.called_at >= start_of_day
    ).count()

    return call_count >= max_calls
