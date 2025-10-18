
import pytest
from models import db, Review, Prescription, User, Medicine
from datetime import datetime

def test_create_review(app):
    with app.app_context():
        user = User(email='testuser@example.com', password='hashed', name='Test User', role='user')
        medicine = Medicine(name='TestMed', generic_name='TestGen', description='Test Desc')
        db.session.add(user)
        db.session.add(medicine)
        db.session.commit()

        review = Review(user_id=user.id, medicine_id=medicine.id, rating=4, comment='Good medicine')
        db.session.add(review)
        db.session.commit()

        assert review.id is not None
        assert review.rating == 4
        assert review.comment == 'Good medicine'
        assert isinstance(review.created_at, datetime)

def test_create_prescription(app):
    with app.app_context():
        user = User.query.filter_by(email='testuser@example.com').first()
        if not user:
            user = User(email='testuser@example.com', password='hashed', name='Test User', role='user')
            db.session.add(user)
            db.session.commit()

        prescription = Prescription(user_id=user.id, image_path='path/to/image.jpg', extracted_text='Sample text')
        db.session.add(prescription)
        db.session.commit()

        assert prescription.id is not None
        assert prescription.image_path == 'path/to/image.jpg'
        assert prescription.extracted_text == 'Sample text'
        assert isinstance(prescription.created_at, datetime)
