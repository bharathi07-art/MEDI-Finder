from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='customer')  # 'customer', 'pharmacy_admin'
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', back_populates='user', cascade='all, delete-orphan')
