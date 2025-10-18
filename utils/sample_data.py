from models import db, Medicine, Pharmacy, PharmacyMedicine, User
from werkzeug.security import generate_password_hash

def add_sample_data():
    """Add sample data for testing"""
    
    # Add sample medicines
    medicines = [
        Medicine(name='Paracetamol', generic_name='Acetaminophen', description='Pain reliever and fever reducer'),
        Medicine(name='Amoxicillin', generic_name='Amoxicillin', description='Antibiotic'),
        Medicine(name='Aspirin', generic_name='Acetylsalicylic acid', description='Pain reliever'),
        Medicine(name='Ibuprofen', generic_name='Ibuprofen', description='NSAID pain reliever'),
        Medicine(name='Metformin', generic_name='Metformin', description='Diabetes medication'),
    ]
    
    for medicine in medicines:
        db.session.add(medicine)
    
    # Add sample pharmacies
    pharmacies = [
        Pharmacy(
            name='City Pharmacy', 
            address='123 Main St, City', 
            latitude=12.9716, 
            longitude=77.5946,
            contact_number='+1234567890',
            is_verified=True
        ),
        Pharmacy(
            name='MedPlus', 
            address='456 Oak Ave, Town', 
            latitude=12.9689, 
            longitude=77.5944,
            contact_number='+0987654321',
            is_verified=True
        ),
    ]
    
    for pharmacy in pharmacies:
        db.session.add(pharmacy)
    
    db.session.commit()
    
    # Add pharmacy staff if not exists
    existing_admin = User.query.filter_by(email='admin@citypharmacy.com').first()
    if not existing_admin:
        pharmacy_admin = User(
            email='admin@citypharmacy.com',
            password=generate_password_hash('password123'),
            name='Pharmacy Admin',
            role='pharmacy_admin',
            pharmacy_id=1
        )
        db.session.add(pharmacy_admin)
    
    # Add medicine availability
    availability = [
        PharmacyMedicine(pharmacy_id=1, medicine_id=1, price=5.99, stock=100),
        PharmacyMedicine(pharmacy_id=1, medicine_id=2, price=15.50, stock=25),
        PharmacyMedicine(pharmacy_id=2, medicine_id=1, price=4.99, stock=50),
        PharmacyMedicine(pharmacy_id=2, medicine_id=3, price=8.75, stock=30),
    ]
    
    for avail in availability:
        db.session.add(avail)
    
    db.session.commit()
    print("Sample data added successfully!")
