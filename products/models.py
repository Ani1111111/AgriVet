from database import db
from sqlalchemy.sql import func

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text)
    animal_type = db.Column(db.String(50))    # e.g., "cattle", "poultry", "canine"
    category = db.Column(db.String(50))       # e.g., "calcium", "vitamin", "feed"
    dosage_info = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
