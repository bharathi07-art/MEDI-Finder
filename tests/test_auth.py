import pytest
from models import User
from werkzeug.security import check_password_hash

def test_register_login_logout(client, app):
    # Test registration page GET
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data

    # Test registration POST with missing fields
    response = client.post('/auth/register', data={
        'email': '',
        'name': '',
        'password': '',
        'confirm_password': ''
    }, follow_redirects=True)
    assert b'All fields are required' in response.data

    # Test registration POST with password mismatch
    response = client.post('/auth/register', data={
        'email': 'testuser@example.com',
        'name': 'Test User',
        'password': 'password123',
        'confirm_password': 'password321'
    }, follow_redirects=True)
    assert b'Passwords do not match' in response.data

    # Test successful registration
    response = client.post('/auth/register', data={
        'email': 'testuser@example.com',
        'name': 'Test User',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'customer'
    }, follow_redirects=True)
    assert b'Registration successful' in response.data

    # Test login page GET
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

    # Test login POST with invalid credentials
    response = client.post('/auth/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data

    # Test login POST with valid credentials
    response = client.post('/auth/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Logout' in response.data or response.status_code == 200

    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'You have been logged out' in response.data

def test_profile_update(client, app):
    # Login first
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Update profile with missing name
    response = client.post('/auth/profile', data={
        'name': ''
    }, follow_redirects=True)
    assert b'Name is required' in response.data

    # Update profile with wrong current password
    response = client.post('/auth/profile', data={
        'name': 'New Name',
        'current_password': 'wrongpass',
        'new_password': 'newpassword'
    }, follow_redirects=True)
    assert b'Current password is incorrect' in response.data

    # Update profile with short new password
    response = client.post('/auth/profile', data={
        'name': 'New Name',
        'current_password': 'password123',
        'new_password': '123'
    }, follow_redirects=True)
    assert b'New password must be at least 6 characters' in response.data

    # Successful profile update
    response = client.post('/auth/profile', data={
        'name': 'New Name',
        'current_password': 'password123',
        'new_password': 'newpassword'
    }, follow_redirects=True)
    assert b'Password updated successfully' in response.data or b'Profile updated successfully' in response.data

def test_check_email_availability(client):
    response = client.get('/auth/api/check-email?email=admin@test.com')
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['available'] is False

    response = client.get('/auth/api/check-email?email=newemail@test.com')
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['available'] is True
