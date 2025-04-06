from app import db
from datetime import datetime

class AlertLog(db.Model):
    __tablename__ = 'alert_logs'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    community_owner_id = db.Column(db.Integer, db.ForeignKey('community_owners.id'), nullable=False)
