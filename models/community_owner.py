# models/community_owner.py
from app import db


class CommunityOwner(db.Model):
    __tablename__ = 'community_owners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    community_name = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    unique_link = db.Column(db.String(256), unique=True, nullable=False)
    telegram_bot_username = db.Column(db.String(64), default='@AlertBySyncgramBot')
    group_chat_id = db.Column(db.BigInteger, nullable=True)  # New field for mapping

    subscribers = db.relationship('Subscriber', backref='owner', lazy=True)
    alert_logs = db.relationship('AlertLog', backref='owner', lazy=True)
