# backend/routes/twilio.py
from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse
import logging
from utils.twilio_utils import initiate_twilio_call

twilio_bp = Blueprint('twilio_bp', __name__)

# Global dictionary to track retry attempts by phone number.
RETRY_ATTEMPTS = {}
MAX_RETRIES = 2  # Adjust as needed

@twilio_bp.route('/voice', methods=['GET', 'POST'])
def voice():
    # Retrieve the message to speak from query parameters
    msg = request.args.get('This is an alert from AlertBySyncgram.')
    logging.info("Generating TwiML voice response with message: %s", msg)
    
    response = VoiceResponse()
    response.say(msg, voice='alice')
    
    # Log the generated TwiML for debugging
    logging.debug("Generated TwiML: %s", response)
    return Response(str(response), mimetype='text/xml')

@twilio_bp.route('/status_callback', methods=['POST'])
def status_callback():
    call_status = request.values.get('CallStatus', '')
    to_number = request.values.get('To', '')
    logging.info("Received Twilio status callback for number %s: %s", to_number, call_status)
    
    # Define the statuses that indicate a failed call
    failed_statuses = ['no-answer', 'failed', 'busy']
    if call_status in failed_statuses:
        # Get the current retry count for this number
        current_attempt = RETRY_ATTEMPTS.get(to_number, 0)
        if current_attempt < MAX_RETRIES:
            RETRY_ATTEMPTS[to_number] = current_attempt + 1
            logging.info("Retrying call to %s (attempt %s)", to_number, current_attempt + 1)
            try:
                # Retry the call.
                # Here we use a default message; ideally, you would reuse the original alert message.
                new_call_sid = initiate_twilio_call(to_number, "Alert signal: please check for new update")
                logging.info("Retry call initiated to %s, new Call SID: %s", to_number, new_call_sid)
            except Exception as e:
                logging.exception("Retry failed for %s", to_number)
        else:
            logging.warning("Max retry attempts reached for %s", to_number)
    else:
        # If the call was successful, clear any retry count for this number
        if to_number in RETRY_ATTEMPTS:
            logging.debug("Clearing retry attempts for %s after successful call", to_number)
            del RETRY_ATTEMPTS[to_number]
    
    return ('', 204)
