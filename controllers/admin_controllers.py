from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, ParkingLot, ParkingStatus, ParkingRecord
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('admin'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('adminDashboard.html')

@admin_bp.route('/addParkingLot', methods=['GET', 'POST'])
@admin_required
def add_parking_lot():
    error = None
    if request.method == 'POST':
        location = request.form.get('location')
        address = request.form.get('address')
        pin = request.form.get('pin')
        spots = request.form.get('spots')
        price = request.form.get('price')
        if not all([location, address, pin, spots, price]):
            error = "All fields are required!"
        elif not (pin.isdigit() and len(pin) == 6):
            error = "Pin code must be a 6-digit number!"
        if not error:
            new_lot = ParkingLot(location=location, address=address, pin=int(pin), total_spots=int(spots), price=float(price))
            db.session.add(new_lot)
            db.session.commit()
            new_status = ParkingStatus(id=new_lot.id, filledCount=0)
            db.session.add(new_status)
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
    return render_template('addParkingLot.html', error=error)

@admin_bp.route('/viewParkingLots')
@admin_required
def view_parking_lots():
    parking_lots = ParkingLot.query.all()
    return render_template('viewParkingLots.html', parking_lots=parking_lots)

@admin_bp.route('/editParkingLot/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot: return "Parking lot not found!", 404
    error = None
    if request.method == 'POST':
        try:
            new_spots = int(request.form.get('spots'))
            new_price = float(request.form.get('price'))
        except (TypeError, ValueError): return "Invalid input!", 400
        occupied = lot.status.filledCount if lot.status else 0
        if new_spots < occupied:
            error = f"Cannot set spots less than currently occupied ({occupied})!"
        else:
            lot.total_spots = new_spots
            lot.price = new_price
            db.session.commit()
            return redirect(url_for('admin.view_parking_lots'))
    return render_template('editParkingLot.html', lot=lot, error=error)

@admin_bp.route('/deleteParkingLot/<int:lot_id>', methods=['POST'])
@admin_required
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot: return "Parking lot not found!", 404
    if lot.status and lot.status.filledCount > 0:
        return "Cannot delete occupied parking lot!", 400
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('admin.view_parking_lots'))

@admin_bp.route('/users')
@admin_required
def users():
    users = User.query.filter_by(admin=False).all()
    return render_template('users.html', users=users)

@admin_bp.route('/search', methods=['GET', 'POST'])
@admin_required
def search():
    results = None
    if request.method == 'POST':
        location = request.form.get('location')
        pin = request.form.get('pin')
        query = ParkingLot.query
        if location: query = query.filter(ParkingLot.location.ilike(f"%{location}%"))
        if pin: query = query.filter(ParkingLot.pin == int(pin))
        results = query.all()
    return render_template('search.html', results=results) 