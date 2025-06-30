from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, ParkingLot, ParkingRecord, ParkingSpot
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
    parking_lots = ParkingLot.query.all()
    return render_template('adminDashboard.html', parking_lots=parking_lots)

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
            db.session.commit() # Commit to get new_lot.id
            for i in range(1, int(spots) + 1):
                spot = ParkingSpot(lot_id=new_lot.id, spot_number=i, status='A')
                db.session.add(spot)
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
    lot = ParkingLot.query.get_or_404(lot_id)
    error = None
    if request.method == 'POST':
        new_total_spots = int(request.form['total_spots'])
        
        lot.location = request.form['location']
        lot.address = request.form['address']
        lot.pin = int(request.form['pin'])
        lot.price = float(request.form['price'])
        
        current_spots = lot.total_spots
        occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()

        if new_total_spots < occupied_spots_count:
            error = f"Cannot reduce spots below the number of occupied spots ({occupied_spots_count})."
        else:
            if new_total_spots > current_spots:
                for i in range(current_spots + 1, new_total_spots + 1):
                    new_spot = ParkingSpot(lot_id=lot_id, spot_number=i, status='A')
                    db.session.add(new_spot)
            elif new_total_spots < current_spots:
                spots_to_delete_count = current_spots - new_total_spots
                available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.spot_number.desc()).limit(spots_to_delete_count).all()
                for spot in available_spots:
                    db.session.delete(spot)
            
            lot.total_spots = new_total_spots
            db.session.commit()
            return redirect(url_for('admin.dashboard'))

    return render_template('editParkingLot.html', lot=lot, error=error)

@admin_bp.route('/deleteParkingLot/<int:lot_id>', methods=['POST'])
@admin_required
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied_spots > 0:
        return "Cannot delete a parking lot with occupied spots!", 400
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

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

@admin_bp.route('/deleteSpot/<int:spot_id>', methods=['POST'])
@admin_required
def delete_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return "Spot not found!", 404
    lot = ParkingLot.query.get(spot.lot_id)
    db.session.delete(spot)
    db.session.commit()
    # Decrement total_spots
    if lot and lot.total_spots > 0:
        lot.total_spots -= 1
        db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/spotDetails/<int:spot_id>')
@admin_required
def spot_details(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return "Spot not found!", 404
    # Get the active booking for this spot (no exit_time)
    record = None
    if spot.status == 'O':
        record = ParkingRecord.query.filter_by(spot_id=spot.id, exit_time=None).first()
    return render_template('spotDetails.html', spot=spot, record=record)

@admin_bp.route('/summary')
@admin_required
def summary():
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    stats = {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': total_spots - occupied_spots
    }
    return render_template('adminSummary.html', stats=stats) 