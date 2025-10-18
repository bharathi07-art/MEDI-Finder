import pytest
from models import PharmacyMedicine

def test_pharmacy_dashboard_access(client):
    # Test access without login
    response = client.get('/pharmacy/dashboard')
    assert response.status_code == 302  # Redirect to login

    # Login as pharmacy admin directly
    login_response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_response.status_code == 200

    # Test access as pharmacy admin
    response = client.get('/pharmacy/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Pharmacy' in response.data

def test_update_stock(client):
    # Login as pharmacy admin
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Test update stock with missing fields
    response = client.post('/pharmacy/update-stock', data={}, follow_redirects=True)
    assert b'Medicine name or ID is required' in response.data

    # Test update stock with invalid data
    response = client.post('/pharmacy/update-stock', data={
        'medicine_id': '1',
        'price': 'invalid',
        'stock': 'invalid'
    }, follow_redirects=True)
    assert b'Invalid price or stock value' in response.data

    # Test successful stock update
    response = client.post('/pharmacy/update-stock', data={
        'medicine_id': '1',
        'price': '10.99',
        'stock': '50'
    }, follow_redirects=True)
    assert b'Stock updated successfully' in response.data

def test_bulk_update_stock(client):
    # Login as pharmacy admin
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Test bulk update with valid data
    response = client.post('/pharmacy/bulk-update-stock', data={
        'stock_1': '75',
        'price_1': '12.50',
        'stock_2': '25',
        'price_2': '18.75'
    }, follow_redirects=True)
    assert b'Successfully updated' in response.data

def test_pharmacy_statistics(client):
    # Login as pharmacy admin
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Check dashboard for statistics
    response = client.get('/pharmacy/dashboard')
    assert response.status_code == 200
    # Statistics should be displayed (total medicines, in stock, etc.)
    assert b'medicines' in response.data.lower()
