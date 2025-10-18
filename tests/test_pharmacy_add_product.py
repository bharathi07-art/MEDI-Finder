import pytest
from flask import url_for
from models import PharmacyMedicine

@pytest.mark.usefixtures("client", "app")
class TestPharmacyAddProduct:

    def test_add_new_product(self, client):
        # Login as pharmacy admin first
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Add new product with price and stock
        response = client.post(url_for('pharmacy.update_stock'), data={
            'medicine_id': 1,
            'price': '100.50',
            'stock': '20'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Check that the success message is in the response
        assert b'Stock updated successfully' in response.data

        # Verify the product was added in the database
        pm = PharmacyMedicine.query.filter_by(
            pharmacy_id=1,  # Assuming test pharmacy id is 1
            medicine_id=1
        ).first()
        assert pm is not None
        assert pm.price == 100.50
        assert pm.stock == 20
        assert pm.is_available is True

    def test_add_product_missing_fields(self, client):
        # Login as pharmacy admin first
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Missing price
        response = client.post(url_for('pharmacy.update_stock'), data={
            'medicine_id': 1,
            'stock': '10'
        })
        assert response.status_code == 200  # Returns HTML with error message
        assert b'All fields are required' in response.data

        # Missing stock
        response = client.post(url_for('pharmacy.update_stock'), data={
            'medicine_id': 1,
            'price': '50'
        })
        assert response.status_code == 200  # Returns HTML with error message
        assert b'All fields are required' in response.data

        # Missing medicine_id
        response = client.post(url_for('pharmacy.update_stock'), data={
            'price': '50',
            'stock': '10'
        })
        assert response.status_code == 200  # Returns HTML with error message
        assert b'Medicine name or ID is required' in response.data

    def test_add_product_invalid_values(self, client):
        # Login as pharmacy admin first
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Invalid price
        response = client.post(url_for('pharmacy.update_stock'), data={
            'medicine_id': 1,
            'price': 'invalid',
            'stock': '10'
        })
        assert response.status_code == 200  # Returns HTML with error message
        assert b'Invalid price or stock value' in response.data

        # Invalid stock
        response = client.post(url_for('pharmacy.update_stock'), data={
            'medicine_id': 1,
            'price': '50',
            'stock': 'invalid'
        })
        assert response.status_code == 200  # Returns HTML with error message
        assert b'Invalid price or stock value' in response.data
