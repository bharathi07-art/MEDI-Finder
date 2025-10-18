from . import db

class Pharmacy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    contact_number = db.Column(db.String(15))
    email = db.Column(db.String(100))
    opening_hours = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    medicines = db.relationship('PharmacyMedicine', backref='pharmacy', lazy=True)
    staff = db.relationship('User', backref='pharmacy_info', lazy=True)
    
    def __repr__(self):
        return f'<Pharmacy {self.name}>'