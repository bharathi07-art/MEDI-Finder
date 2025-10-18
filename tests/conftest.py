import pytest
import os
import tempfile
from app import create_app, db
from models import User, Medicine, Pharmacy, PharmacyMedicine
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        # Add test data
        _add_test_data()

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def _add_test_data():
    """Add sample test data."""
    # Clear any existing data first
    db.session.query(PharmacyMedicine).delete()
    db.session.query(User).delete()
    db.session.query(Pharmacy).delete()
    db.session.query(Medicine).delete()
    db.session.commit()

    # Create test medicines
    medicine1 = Medicine(name='Paracetamol', generic_name='Acetaminophen', description='Pain reliever')
    medicine2 = Medicine(name='Amoxicillin', generic_name='Amoxicillin', description='Antibiotic')
    db.session.add_all([medicine1, medicine2])

    # Create test pharmacy
    pharmacy = Pharmacy(
        name='Test Pharmacy',
        address='123 Test St, Test City',
        latitude=12.9716,
        longitude=77.5946,
        contact_number='+1234567890',
        is_verified=True
    )
    db.session.add(pharmacy)
    db.session.commit()

    # Create pharmacy admin user
    admin_user = User(
        email='admin@test.com',
        password=generate_password_hash('password123'),
        name='Test Admin',
        role='pharmacy_admin',
        pharmacy_id=pharmacy.id
    )
    db.session.add(admin_user)

    # Create regular user
    regular_user = User(
        email='user@test.com',
        password=generate_password_hash('password123'),
        name='Test User',
        role='customer'
    )
    db.session.add(regular_user)

    # Create pharmacy medicine availability
    pm1 = PharmacyMedicine(
        pharmacy_id=pharmacy.id,
        medicine_id=medicine1.id,
        price=5.99,
        stock=100,
        is_available=True
    )
    pm2 = PharmacyMedicine(
        pharmacy_id=pharmacy.id,
        medicine_id=medicine2.id,
        price=15.50,
        stock=25,
        is_available=True
    )
    db.session.add_all([pm1, pm2])
    db.session.commit()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for a logged-in user."""
    # Login as regular user
    response = client.post('/auth/login', data={
        'email': 'user@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    # For simplicity, we'll use session-based auth
    # In a real scenario, you might need to extract tokens
    return {}

@pytest.fixture
def admin_auth_headers(client):
    """Get authentication headers for a logged-in admin user."""
    # Login as admin user
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    return {}
