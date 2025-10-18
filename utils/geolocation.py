import os
import requests
from geopy.distance import geodesic

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    if None in [lat1, lon1, lat2, lon2]:
        return None
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_coordinates_from_address(address):
    """Get latitude and longitude from address using free geocoding services"""

    # First try Google Maps API if key is available
    if GOOGLE_MAPS_API_KEY:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'OK' and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return (location['lat'], location['lng'])
        except Exception as e:
            print(f"Google Maps API error: {e}")

    # Fallback to free Nominatim (OpenStreetMap) API
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "user-agent": "medifinder_app"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return (float(data[0]['lat']), float(data[0]['lon']))
        else:
            return (None, None)
    except Exception as e:
        print(f"Nominatim geocoding error: {e}")
        return (None, None)
