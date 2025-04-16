from datetime import datetime, timezone

from app import db


class CallLog(db.Model):
    __tablename__ = 'call_logs'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    called_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
