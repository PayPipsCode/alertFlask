from app import db
from datetime import datetime, timezone


class AlertLog(db.Model):
    __tablename__ = 'alert_logs'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))
    community_owner_id = db.Column(db.Integer, db.ForeignKey('community_owners.id'), nullable=False)
