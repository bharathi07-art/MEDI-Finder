from flask import jsonify

def json_response(message, data=None, status=200):
    """Standard JSON response format"""
    response = {
        'status': 'success' if status < 400 else 'error',
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status

def validate_coordinates(lat, lng):
    """Validate latitude and longitude values"""
    try:
        lat = float(lat)
        lng = float(lng)
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return True, lat, lng
        return False, None, None
    except (ValueError, TypeError):
        return False, None, None