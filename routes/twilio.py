from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse
import logging

twilio_bp = Blueprint('twilio_bp', __name__)

@twilio_bp.route('/voice', methods=['GET', 'POST'])
def voice():
    # Retrieve the message to speak from query parameters
    msg = request.args.get('msg', 'This is an alert from AlertBySyncgram.')
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
    return ('', 204)
