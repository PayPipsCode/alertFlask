import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    DEBUG = os.environ.get('DEBUG', True)
    
    # Database configuration

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:TTGAMLWDBwoNOsrdGHnZgVEinNyBiwzH@caboose.proxy.rlwy.net:31157/railway'
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



