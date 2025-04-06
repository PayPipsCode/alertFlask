from app import db

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(32), default='pending')
    payment_plan = db.Column(db.String(32), nullable=True)  # 'Basic' or 'Standard'
    
    community_owner_id = db.Column(db.Integer, db.ForeignKey('community_owners.id'), nullable=False)
