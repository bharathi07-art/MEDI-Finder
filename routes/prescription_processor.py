from flask import Blueprint, request, jsonify, current_app
from models.prescription import Prescription
from models import db
from utils.ocr_processor import get_ocr_processor
from utils.medicine_parser import get_medicine_parser
import os
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

prescription_bp = Blueprint('prescription_processor', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@prescription_bp.route('/process-prescription', methods=['POST'])
def process_prescription():
    """Process uploaded prescription image"""
    try:
        # Check if file is present
        if 'prescription' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['prescription']

        # Check if file is selected
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'File type not allowed. Use PNG, JPG, JPEG, or PDF'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'status': 'error', 'message': 'File too large. Maximum size is 16MB'}), 400

        # Get user ID (for now, use a default or get from session)
        # TODO: Get actual user ID from authentication
        user_id = 1  # Default user for now

        # Save uploaded file
        ocr_processor = get_ocr_processor()
        file_path = ocr_processor.save_uploaded_file(file)

        if not file_path:
            return jsonify({'status': 'error', 'message': 'Failed to save file'}), 500

        # Create prescription record
        prescription = Prescription(
            user_id=user_id,
            image_path=file_path,
            processing_status='processing'
        )
        db.session.add(prescription)
        db.session.commit()

        # Process the prescription asynchronously (for now, process synchronously)
        try:
            # Extract text using OCR
            extracted_text = ocr_processor.extract_text(file_path)

            if not extracted_text:
                prescription.processing_status = 'failed'
                prescription.extracted_text = 'Could not extract text from image. Please ensure the image is clear and try again.'
                db.session.commit()
                return jsonify({'status': 'error', 'message': 'Could not extract text from prescription'}), 400

            # Parse medicines from extracted text
            medicine_parser = get_medicine_parser()
            parsed_medicines = medicine_parser.parse_text(extracted_text)

            # Update prescription with results
            prescription.extracted_text = extracted_text
            prescription.set_parsed_medicines(parsed_medicines)
            prescription.processing_status = 'completed'

            db.session.commit()

            # Format response
            response_data = {
                'status': 'success',
                'message': 'Prescription processed successfully',
                'data': {
                    'prescription_id': prescription.id,
                    'extracted_text': extracted_text,
                    'medicines': parsed_medicines,
                    'formatted_medicines': prescription.get_formatted_medicines()
                }
            }

            return jsonify(response_data), 200

        except Exception as e:
            logger.error(f"Error processing prescription: {str(e)}")
            prescription.processing_status = 'failed'
            prescription.extracted_text = f'Error processing prescription: {str(e)}'
            db.session.commit()
            return jsonify({'status': 'error', 'message': 'Failed to process prescription'}), 500

    except Exception as e:
        logger.error(f"Error in process_prescription: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@prescription_bp.route('/prescription/<int:prescription_id>', methods=['GET'])
def get_prescription_results(prescription_id):
    """Get prescription processing results"""
    try:
        prescription = Prescription.query.get(prescription_id)

        if not prescription:
            return jsonify({'status': 'error', 'message': 'Prescription not found'}), 404

        response_data = {
            'status': 'success',
            'data': {
                'prescription_id': prescription.id,
                'processing_status': prescription.processing_status,
                'extracted_text': prescription.extracted_text,
                'medicines': prescription.get_parsed_medicines(),
                'formatted_medicines': prescription.get_formatted_medicines(),
                'created_at': prescription.created_at.isoformat()
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error getting prescription results: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@prescription_bp.route('/search-pharmacies', methods=['POST'])
def search_pharmacies_for_medicines():
    """Search for pharmacies that have the specified medicines"""
    try:
        data = request.get_json()

        if not data or 'medicines' not in data:
            return jsonify({'status': 'error', 'message': 'Medicines list required'}), 400

        medicines = data['medicines']
        user_lat = data.get('lat')
        user_lng = data.get('lng')
        max_distance = data.get('distance', 10)

        if not medicines:
            return jsonify({'status': 'error', 'message': 'No medicines provided'}), 400

        # Import search functionality
        from routes.search import search_bp
        from utils.geolocation import calculate_distance
        from models import Medicine, Pharmacy, PharmacyMedicine

        # Get all medicines from database
        all_medicines = {med.name.lower(): med for med in Medicine.query.all()}

        results = []

        for medicine_name in medicines:
            # Try to find medicine in database (case insensitive)
            medicine = None
            for db_med_name, db_med in all_medicines.items():
                if db_med_name in medicine_name.lower() or medicine_name.lower() in db_med_name:
                    medicine = db_med
                    break

            if not medicine:
                # If medicine not found, try standardized name matching
                standardized_name = medicine_name.title()
                medicine = Medicine.query.filter(
                    Medicine.name.ilike(f'%{standardized_name}%')
                ).first()

            if medicine:
                # Find pharmacies that have this medicine
                availabilities = PharmacyMedicine.query.filter_by(
                    medicine_id=medicine.id,
                    is_available=True
                ).all()

                for availability in availabilities:
                    pharmacy = Pharmacy.query.get(availability.pharmacy_id)

                    # Calculate distance if coordinates provided
                    distance = None
                    if user_lat and user_lng and pharmacy.latitude and pharmacy.longitude:
                        distance = calculate_distance(
                            float(user_lat), float(user_lng),
                            pharmacy.latitude, pharmacy.longitude
                        )

                        # Skip if beyond max distance
                        if distance > max_distance:
                            continue

                    results.append({
                        'medicine': {
                            'id': medicine.id,
                            'name': medicine.name,
                            'generic_name': medicine.generic_name,
                            'searched_name': medicine_name
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

        return jsonify({
            'status': 'success',
            'message': f'Found {len(results)} pharmacy matches',
            'data': {'results': results}
        }), 200

    except Exception as e:
        logger.error(f"Error searching pharmacies: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
