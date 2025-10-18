import pytest
from models import Medicine, Pharmacy

def test_search_medicines_api(client):
    # Test search without parameters
    response = client.get('/api/search')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'results' in data['data']

    # Test search with medicine name
    response = client.get('/api/search?medicine=Paracetamol')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']['results']) > 0

    # Test search with location
    response = client.get('/api/search?medicine=Paracetamol&lat=12.9716&lng=77.5946&distance=10')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'

    # Test search with invalid coordinates
    response = client.get('/api/search?medicine=Paracetamol&lat=invalid&lng=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

    # Test search with no results
    response = client.get('/api/search?medicine=NonExistentMedicine')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']['results']) == 0

def test_nearby_pharmacies_api(client):
    # Test nearby pharmacies without coordinates
    response = client.get('/api/nearby-pharmacies')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

    # Test nearby pharmacies with valid coordinates
    response = client.get('/api/nearby-pharmacies?lat=12.9716&lng=77.5946&distance=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'pharmacies' in data['data']

    # Test nearby pharmacies with invalid coordinates
    response = client.get('/api/nearby-pharmacies?lat=invalid&lng=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

def test_search_page_rendering(client):
    # Test search page loads
    response = client.get('/search')
    assert response.status_code == 200
    assert b'Search Medicines' in response.data
    assert b'Enter medicine name' in response.data

def test_homepage_rendering(client):
    # Test homepage loads
    response = client.get('/')
    assert response.status_code == 200
    assert b'Find Medicines Near You' in response.data
    assert b'Search Medicines' in response.data
