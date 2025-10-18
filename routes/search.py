from flask import Blueprint, request, render_template, jsonify
from models import Medicine, Pharmacy, PharmacyMedicine, db
from utils.geolocation import calculate_distance
from utils.helpers import json_response, validate_coordinates

# Import get_coordinates_from_address here to avoid import error
import utils.geolocation as geolocation_utils

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_medicines():
    """Search for medicines with location filtering"""
    medicine_name = request.args.get('medicine', '')
    user_lat = request.args.get('lat')
    user_lng = request.args.get('lng')
    max_distance = request.args.get('distance', 10, type=float)
    
    # Validate coordinates
    if user_lat and user_lng:
        valid, lat, lng = validate_coordinates(user_lat, user_lng)
        if not valid:
            return json_response('Invalid coordinates provided', status=400)
    
    # Search for medicines
    medicines = Medicine.query.filter(
        Medicine.name.ilike(f'%{medicine_name}%')
    ).all()
    
    results = []
    for medicine in medicines:
        # Find pharmacies that have this medicine
        availabilities = PharmacyMedicine.query.filter_by(
            medicine_id=medicine.id,
            is_available=True
        ).all()
        
        for availability in availabilities:
            pharmacy = db.session.get(Pharmacy, availability.pharmacy_id)
            if not pharmacy:
                continue

            # Calculate distance if coordinates provided
            distance = None
            if user_lat and user_lng and pharmacy.latitude and pharmacy.longitude:
                distance = calculate_distance(
                    float(user_lat), float(user_lng),
                    pharmacy.latitude, pharmacy.longitude
                )

                # Skip if beyond max distance
            if distance is not None and distance > max_distance:
                continue

            results.append({
                'medicine': {
                    'id': medicine.id,
                    'name': medicine.name,
                    'generic_name': medicine.generic_name
                },
                'pharmacy': {
                    'id': pharmacy.id,
                    'name': pharmacy.name,
                    'address': pharmacy.address,
                    'latitude': pharmacy.latitude,
                    'longitude': pharmacy.longitude,
                    'contact': pharmacy.contact_number
                },
                'availability': {
                    'price': availability.price,
                    'stock': availability.stock,
                    'last_updated': availability.last_updated.isoformat()
                },
                'distance': distance
            })
    
    # Sort by distance if available
    if user_lat and user_lng:
        results.sort(key=lambda x: x['distance'] or float('inf'))
    
    return json_response('Search results', {'results': results})

@search_bp.route('/nearby-pharmacies', methods=['GET'])
def nearby_pharmacies():
    """Get pharmacies near user location"""
    user_lat = request.args.get('lat')
    user_lng = request.args.get('lng')
    max_distance = request.args.get('distance', 5, type=float)
    
    valid, lat, lng = validate_coordinates(user_lat, user_lng)
    if not valid:
        return json_response('Valid coordinates required', status=400)
    
    pharmacies = Pharmacy.query.filter(
        Pharmacy.latitude.isnot(None),
        Pharmacy.longitude.isnot(None),
        Pharmacy.is_verified == True
    ).all()
    
    nearby = []
    for pharmacy in pharmacies:
        distance = calculate_distance(lat, lng, pharmacy.latitude, pharmacy.longitude)
        if distance is not None and distance <= max_distance:
            nearby.append({
                'id': pharmacy.id,
                'name': pharmacy.name,
                'address': pharmacy.address,
                'latitude': pharmacy.latitude,
                'longitude': pharmacy.longitude,
                'contact': pharmacy.contact_number,
                'distance': round(distance, 2)
            })
    
    nearby.sort(key=lambda x: x['distance'])
    return json_response('Nearby pharmacies', {'pharmacies': nearby})

@search_bp.route('/geocode', methods=['GET'])
def geocode_address():
    """Geocode an address to latitude and longitude"""
    address = request.args.get('address')
    if not address:
        return jsonify({'status': 'error', 'message': 'Address parameter is required'}), 400
    
    lat, lng = geolocation_utils.get_coordinates_from_address(address)
    if lat is None or lng is None:
        return jsonify({'status': 'error', 'message': 'Could not geocode address'}), 404
    
    return jsonify({'status': 'success', 'data': {'lat': lat, 'lng': lng}})
