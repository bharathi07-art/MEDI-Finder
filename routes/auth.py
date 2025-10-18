from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Pharmacy
from utils.helpers import json_response
from utils.geolocation import get_coordinates_from_address
from datetime import datetime, timezone

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Simple form class for profile
class ProfileForm:
    def __init__(self):
        self.name = None
        self.current_password = None
        self.new_password = None

    def validate_on_submit(self):
        self.name = request.form.get('name')
        self.current_password = request.form.get('current_password')
        self.new_password = request.form.get('new_password')

        if not self.name:
            flash('Name is required', 'error')
            return False

        if self.current_password and not self.new_password:
            flash('New password is required when changing password', 'error')
            return False

        if self.new_password and len(self.new_password) < 6:
            flash('New password must be at least 6 characters', 'error')
            return False

        return True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type', 'customer')
        
        # Validation
        errors = []
        
        if not all([email, name, password, confirm_password]):
            errors.append('All fields are required')
        
        if password != confirm_password:
            errors.append('Passwords do not match')

        if password and len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('auth.login'))
        
        # Pharmacy-specific validation
        pharmacy_data = None
        if user_type == 'pharmacy_admin':
            pharmacy_name = request.form.get('pharmacy_name')
            pharmacy_address = request.form.get('pharmacy_address')
            pharmacy_contact = request.form.get('pharmacy_contact')
            
            if not all([pharmacy_name, pharmacy_address, pharmacy_contact]):
                errors.append('All pharmacy details are required')
            else:
                pharmacy_data = {
                    'name': pharmacy_name,
                    'address': pharmacy_address,
                    'contact_number': pharmacy_contact
                }
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', 
                                 user_type=user_type,
                                 form_data=request.form)
        
        try:
            # Create user
            if not password:
                errors.append('Password is required')
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(
                    email=email,
                    name=name,
                    password=hashed_password,
                    role=user_type
                )

                # If pharmacy admin, create pharmacy first
                if user_type == 'pharmacy_admin' and pharmacy_data:
                    # Get coordinates from address
                    lat, lng = get_coordinates_from_address(pharmacy_data['address'])

                    new_pharmacy = Pharmacy(
                        name=pharmacy_data['name'],
                        address=pharmacy_data['address'],
                        contact_number=pharmacy_data['contact_number'],
                        latitude=lat,
                        longitude=lng,
                        is_verified=False  # Admin needs to verify later
                    )
                    db.session.add(new_pharmacy)
                    db.session.flush()  # Get the pharmacy ID

                    new_user.pharmacy_id = new_pharmacy.id

                db.session.add(new_user)
                db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html', 
                                 user_type=user_type,
                                 form_data=request.form)
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            
            # Redirect based on user role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'pharmacy_admin':
                return redirect(url_for('pharmacy.pharmacy_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = db.session.get(User, current_user.id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.profile'))

        user.name = form.name

        if form.current_password and form.new_password:
            if not check_password_hash(user.password, form.current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('auth.profile'))

            user.password = generate_password_hash(form.new_password)
            flash('Password updated successfully', 'success')

        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile', 'error')

        return redirect(url_for('auth.profile'))

    # Pre-fill form with current user data
    form.name = current_user.name

    return render_template('auth/profile.html', user=current_user, form=form)

@auth_bp.route('/api/check-email')
def check_email_availability():
    """API endpoint to check email availability"""
    email = request.args.get('email')
    if not email:
        return json_response('Email parameter required', status=400)
    
    user = User.query.filter_by(email=email).first()
    return json_response('Email check successful', {
        'available': user is None,
        'email': email
    })

# Admin routes for user management (optional)
@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin user management (only for super admins)"""
    if current_user.role != 'super_admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/verify-pharmacy/<int:pharmacy_id>')
@login_required
def verify_pharmacy(pharmacy_id):
    """Verify a pharmacy (admin only)"""
    if current_user.role != 'super_admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    pharmacy.is_verified = True
    
    try:
        db.session.commit()
        flash('Pharmacy verified successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error verifying pharmacy', 'error')
    
    return redirect(url_for('auth.admin_users'))