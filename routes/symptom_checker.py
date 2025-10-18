from flask import Blueprint, render_template, request, jsonify
from flask_cors import CORS
from symptom_checker.chat import get_response

symptom_checker_bp = Blueprint('symptom_checker', __name__)
CORS(symptom_checker_bp)

@symptom_checker_bp.route('/')
def index():
    return render_template('symptom_checker/base.html')

@symptom_checker_bp.route('/login')
def login():
    return render_template('symptom_checker/login.html')

@symptom_checker_bp.route('/admin')
def admin():
    return render_template('symptom_checker/admin.html')

@symptom_checker_bp.route('/about')
def about_us():
    return render_template('symptom_checker/about_us.html')

@symptom_checker_bp.route('/predict', methods=['POST'])
def predict():
    text = request.get_json().get("message")
    # TODO: check if text is valid
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

@symptom_checker_bp.route('/prescription_upload')
def prescription_upload():
    return render_template('symptom_checker/prescription_upload.html')
