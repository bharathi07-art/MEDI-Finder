from . import db

class PharmacyMedicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Add relationship to Medicine model
    medicine = db.relationship('Medicine', backref='pharmacy_medicines')

    def __init__(self, pharmacy_id, medicine_id, price, stock, is_available=True):
        self.pharmacy_id = pharmacy_id
        self.medicine_id = medicine_id
        self.price = price
        self.stock = stock
        self.is_available = is_available

    def __repr__(self):
        return f'<Availability {self.pharmacy_id}-{self.medicine_id}>'
