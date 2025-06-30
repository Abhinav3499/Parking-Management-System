from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, ParkingLot, ParkingRecord, ParkingSpot
from datetime import datetime
from math import ceil
from functools import wraps

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('admin'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/')
@user_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('userDashboard.html', username=session['username'], parking_history=user.parking_history)

@user_bp.route('/book', methods=['GET', 'POST'])
@user_required
def book():
    if request.method == 'POST':
        lot_id = request.form.get('lot_id')
        vehicle_number = request.form.get('vehicle_number')
        user_id = session['user_id']
        
        if not lot_id or not vehicle_number:
            return "Missing required information!", 400

        lot = ParkingLot.query.get(lot_id)
        if not lot: return "Parking lot not found!", 404

        available_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').order_by(ParkingSpot.spot_number).first()
        if not available_spot: return "No spots available!", 400

        available_spot.status = 'O'
        
        record = ParkingRecord(
            user_id=user_id, vehicle_number=vehicle_number, parking_time=datetime.now(),
            lot_id=lot.id, price_at_booking=lot.price, lot_location=lot.location, 
            lot_address=lot.address, lot_pin=str(lot.pin), spot_id=available_spot.id
        )
        db.session.add(record)
        db.session.commit()
        
        return redirect(url_for('user.booking_summary', record_id=record.id))

    search_location = request.args.get('location', '')
    search_pin = request.args.get('pin', '')
    query = ParkingLot.query
    if search_location: query = query.filter(ParkingLot.location.ilike(f'%{search_location}%'))
    if search_pin: query = query.filter(ParkingLot.pin.ilike(f'%{search_pin}%'))
    lots = query.all()
    
    return render_template('book.html', lots=lots, search_location=search_location, search_pin=search_pin)

@user_bp.route('/summary/<int:record_id>')
@user_required
def booking_summary(record_id):
    record = ParkingRecord.query.get_or_404(record_id)
    if record.user_id != session['user_id']: return "Unauthorized", 403
    return render_template('summary.html', record=record)

@user_bp.route('/exit/<int:record_id>', methods=['GET', 'POST'])
@user_required
def exit_parking(record_id):
    record = ParkingRecord.query.get_or_404(record_id)
    if record.user_id != session['user_id']: return "Unauthorized", 403

    if request.method == 'POST':
        if record.exit_time is not None: return "Already exited!", 400
        record.exit_time = datetime.now()
        if record.spot:
            record.spot.status = 'A'
        db.session.commit()
        return redirect(url_for('user.history'))

    end_time = datetime.now()
    hours = ceil((end_time - record.parking_time).total_seconds() / 3600)
    total_amount = hours * record.price_at_booking
    
    return render_template('exit.html', record=record, hours=hours, total_amount=total_amount)

@user_bp.route('/history')
@user_required
def history():
    user = User.query.get(session['user_id'])
    return render_template('history.html', history=user.parking_history)

@user_bp.route('/stats')
@user_required
def stats():
    user = User.query.get(session['user_id'])
    history = user.parking_history
    total_bookings = len(history)
    active_bookings = len([r for r in history if r.exit_time is None])
    completed_bookings = total_bookings - active_bookings
    
    location_counts = {}
    for record in history:
        if record.lot:
            location_counts[record.lot_location] = location_counts.get(record.lot_location, 0) + 1
    most_visited = max(location_counts, key=location_counts.get) if location_counts else 'N/A'

    return render_template('stats.html', total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         completed_bookings=completed_bookings,
                         most_visited_location=most_visited) 