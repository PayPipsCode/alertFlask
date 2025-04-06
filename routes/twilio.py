from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse
import logging
from utils.twilio_utils import initiate_twilio_call

twilio_bp = Blueprint('twilio_bp', __name__)

@twilio_bp.route('/voice', methods=['GET', 'POST'])
def voice():
    message = request.args.get('msg', 'Alert message not provided.')
    logging.info(f"Twilio voice endpoint received message: {message}")
    resp = VoiceResponse()
    resp.say(message, voice='alice')
    return Response(str(resp), mimetype='text/xml')

@twilio_bp.route('/status_callback', methods=['POST'])
def status_callback():
    call_status = request.values.get('CallStatus', '')
    to_number = request.values.get('To', '')
    logging.info(f"Twilio status callback: {to_number} status: {call_status}")
    return ('', 204)
