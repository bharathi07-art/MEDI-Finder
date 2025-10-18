from . import db

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    reviews = db.relationship('Review', back_populates='medicine', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Medicine {self.name}>'
