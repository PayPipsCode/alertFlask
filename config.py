import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    DEBUG = os.environ.get('DEBUG', True)
    
    # Database configuration

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Twilio configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Paystack configuration
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
    
    # Telegram Bot token
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    # Base URL (used for callbacks)
    BASE_URL = os.environ.get('BASE_URL')
    KORA_SECRET_KEY = os.environ.get('KORA_SECRET_KEY')

    SYNC_GRAM_AUTH_TOKEN = os.environ.get('SYNC_GRAM_AUTH_TOKEN')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')
    FRONTEND_REDIRECT_URL = os.environ.get('FRONTEND_REDIRECT_URL')
