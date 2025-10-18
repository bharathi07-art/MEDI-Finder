from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Pharmacy, PharmacyMedicine, Medicine, db
from utils.helpers import json_response
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timezone

pharmacy_bp = Blueprint('pharmacy', __name__)

@pharmacy_bp.route('/dashboard')
@login_required
def pharmacy_dashboard():
    """Pharmacy admin dashboard"""

    if current_user.role != 'pharmacy_admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    pharmacy = Pharmacy.query.get_or_404(current_user.pharmacy_id)
    medicines = PharmacyMedicine.query.options(joinedload(PharmacyMedicine.medicine)).filter_by(pharmacy_id=pharmacy.id).all()  # type: ignore

    # Calculate statistics
    total_medicines = len(medicines)
    total_in_stock = sum(1 for m in medicines if m.stock > 0)
    total_out_of_stock = sum(1 for m in medicines if m.stock == 0)
    total_low_stock = sum(1 for m in medicines if 0 < m.stock < 10)

    return render_template('pharmacy/dashboard.html',
                         pharmacy=pharmacy,
                         medicines=medicines,
                         total_medicines=total_medicines,
                         total_in_stock=total_in_stock,
                         total_out_of_stock=total_out_of_stock,
                         total_low_stock=total_low_stock)

@pharmacy_bp.route('/update-stock', methods=['POST'])
@login_required
def update_stock():
    """Update medicine stock and price"""
    if current_user.role != 'pharmacy_admin':
        if request.is_json:
            return json_response('Access denied', status=403)
        else:
            flash('Access denied', 'error')
            return redirect(url_for('pharmacy.pharmacy_dashboard'))

    # Get pharmacy data for error handling
    pharmacy = Pharmacy.query.get_or_404(current_user.pharmacy_id)
    medicines = PharmacyMedicine.query.options(joinedload(PharmacyMedicine.medicine)).filter_by(pharmacy_id=pharmacy.id).all()  # type: ignore
    total_medicines = len(medicines)
    total_in_stock = sum(1 for m in medicines if m.stock > 0)
    total_out_of_stock = sum(1 for m in medicines if m.stock == 0)
    total_low_stock = sum(1 for m in medicines if 0 < m.stock < 10)

    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    medicine_name = data.get('medicine_name')
    medicine_id = data.get('medicine_id')
    price = data.get('price')
    stock = data.get('stock')

    # Support both medicine_name and medicine_id for backward compatibility
    if not medicine_name and not medicine_id:
        if request.is_json:
            return json_response('Medicine name or ID is required', status=400)
        else:
            return render_template('pharmacy/dashboard.html',
                                 pharmacy=pharmacy,
                                 medicines=medicines,
                                 total_medicines=total_medicines,
                                 total_in_stock=total_in_stock,
                                 total_out_of_stock=total_out_of_stock,
                                 total_low_stock=total_low_stock,
                                 error_message='Medicine name or ID is required')

    if not all([price, stock]):
        if request.is_json:
            return json_response('All fields are required', status=400)
        else:
            return render_template('pharmacy/dashboard.html',
                                 pharmacy=pharmacy,
                                 medicines=medicines,
                                 total_medicines=total_medicines,
                                 total_in_stock=total_in_stock,
                                 total_out_of_stock=total_out_of_stock,
                                 total_low_stock=total_low_stock,
                                 error_message='All fields are required')

    try:
        # Find or create medicine
        if medicine_id:
            # Use existing medicine by ID
            medicine = db.session.get(Medicine, medicine_id)
            if not medicine:
                if request.is_json:
                    return json_response('Medicine not found', status=404)
                else:
                    return render_template('pharmacy/dashboard.html',
                                         pharmacy=pharmacy,
                                         medicines=medicines,
                                         total_medicines=total_medicines,
                                         total_in_stock=total_in_stock,
                                         total_out_of_stock=total_out_of_stock,
                                         total_low_stock=total_low_stock,
                                         error_message='Medicine not found')
        else:
            # Find or create medicine by name
            medicine = Medicine.query.filter_by(name=medicine_name).first()
            if not medicine:
                medicine = Medicine(name=medicine_name)
                db.session.add(medicine)
                db.session.flush()  # Get the ID without committing

        price_val = float(price) if price is not None else 0.0
        stock_val = int(stock) if stock is not None else 0

        pm = PharmacyMedicine.query.filter_by(
            pharmacy_id=current_user.pharmacy_id,
            medicine_id=medicine.id
        ).first()

        if pm:
            pm.price = price_val
            pm.stock = stock_val
            pm.is_available = stock_val > 0
        else:
            pm = PharmacyMedicine(
                pharmacy_id=current_user.pharmacy_id,
                medicine_id=medicine.id,
                price=price_val,
                stock=stock_val,
                is_available=stock_val > 0
            )
            db.session.add(pm)

        db.session.commit()

        if request.is_json:
            return json_response('Stock updated successfully')
        else:
            flash('Stock updated successfully', 'success')
            return redirect(url_for('pharmacy.pharmacy_dashboard'))

    except ValueError:
        if request.is_json:
            return json_response('Invalid price or stock value', status=400)
        else:
            # For regular form submissions, return the error message directly
            # instead of redirecting, so tests can check the response
            return render_template('pharmacy/dashboard.html',
                                 pharmacy=pharmacy,
                                 medicines=medicines,
                                 total_medicines=total_medicines,
                                 total_in_stock=total_in_stock,
                                 total_out_of_stock=total_out_of_stock,
                                 total_low_stock=total_low_stock,
                                 error_message='Invalid price or stock value')
    
    
@pharmacy_bp.route('/bulk-update-stock', methods=['POST'])
@login_required
def bulk_update_stock():
    """Bulk update medicine stock and prices"""
    if current_user.role != 'pharmacy_admin':
        if request.is_json:
            return json_response('Access denied', status=403)
        else:
            flash('Access denied', 'error')
            return redirect(url_for('pharmacy.pharmacy_dashboard'))

    try:
        updates = 0
        errors = []

        for key, value in request.form.items():
            if key.startswith('stock_'):
                medicine_id = key.replace('stock_', '')
                price_key = f'price_{medicine_id}'

                if price_key in request.form:
                    price_val = request.form[price_key]
                    stock_val = value

                    # Validate inputs
                    if not stock_val or not price_val:
                        errors.append(f'Missing values for medicine ID {medicine_id}')
                        continue

                    try:
                        stock = int(stock_val)
                        price = float(price_val)

                        if stock < 0:
                            errors.append(f'Invalid stock value for medicine ID {medicine_id}: cannot be negative')
                            continue

                        if price <= 0:
                            errors.append(f'Invalid price value for medicine ID {medicine_id}: must be positive')
                            continue

                    except ValueError:
                        errors.append(f'Invalid numeric values for medicine ID {medicine_id}')
                        continue

                    # Update the record
                    pm = PharmacyMedicine.query.filter_by(
                        pharmacy_id=current_user.pharmacy_id,
                        medicine_id=medicine_id
                    ).first()

                    if pm:
                        pm.stock = stock
                        pm.price = price
                        pm.is_available = stock > 0
                        pm.last_updated = datetime.now(timezone.utc)
                        updates += 1
                    else:
                        errors.append(f'Medicine with ID {medicine_id} not found in your pharmacy')

        db.session.commit()

        if errors:
            message = f'Updated {updates} medicines with {len(errors)} errors: ' + '; '.join(errors[:3])
            if request.is_json:
                return json_response(message, status=400 if updates == 0 else 207)
            else:
                flash(message, 'warning' if updates > 0 else 'error')
                return redirect(url_for('pharmacy.pharmacy_dashboard'))

        message = f'Successfully updated {updates} medicines!'
        if request.is_json:
            return json_response(message)
        else:
            flash(message, 'success')
            return redirect(url_for('pharmacy.pharmacy_dashboard'))

    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return json_response(f'Error updating medicines: {str(e)}', status=500)
        else:
            flash(f'Error updating medicines: {str(e)}', 'error')
            return redirect(url_for('pharmacy.pharmacy_dashboard'))

@pharmacy_bp.route('/sold-medicines')
@login_required
def sold_medicines():
    """Show sold medicines and allow stock updates"""
    if current_user.role != 'pharmacy_admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    pharmacy = Pharmacy.query.get_or_404(current_user.pharmacy_id)
    medicines = PharmacyMedicine.query.options(selectinload(PharmacyMedicine.medicine)).filter_by(pharmacy_id=pharmacy.id).all()  # type: ignore

    # Calculate sold statistics (assuming sold = initial_stock - current_stock, but we don't have initial_stock)
    # For now, show low stock as potentially sold
    sold_medicines = [m for m in medicines if m.stock < 10]  # Consider low stock as sold
    total_sold = sum(m.stock for m in sold_medicines)  # This is not accurate, but placeholder

    return render_template('pharmacy/sold_medicines.html',
                         pharmacy=pharmacy,
                         medicines=medicines,
                         sold_medicines=sold_medicines,
                         total_sold=total_sold)

# New route to delete a product
@pharmacy_bp.route('/delete-product/<int:medicine_id>', methods=['POST'])
@login_required
def delete_product(medicine_id):
    if current_user.role != 'pharmacy_admin':
        flash('Access denied', 'error')
        return redirect(url_for('pharmacy.pharmacy_dashboard'))

    pm = PharmacyMedicine.query.filter_by(
        pharmacy_id=current_user.pharmacy_id,
        medicine_id=medicine_id
    ).first()

    if not pm:
        flash('Product not found', 'error')
        return redirect(url_for('pharmacy.pharmacy_dashboard'))

    try:
        db.session.delete(pm)
        db.session.commit()
        flash('Product deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting product', 'error')

    return redirect(url_for('pharmacy.pharmacy_dashboard'))
