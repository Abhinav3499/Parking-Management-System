from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, ParkingLot, ParkingStatus, ParkingRecord
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
def book_parking():
    locations = [lot.location for lot in ParkingLot.query.all()]
    unique_locations = sorted(list(set(locations)))
    parking_lots = None
    selected_location = None
    if request.method == 'POST':
        selected_location = request.form.get('location')
        if selected_location:
            parking_lots = ParkingLot.query.filter_by(location=selected_location).all()
            for lot in parking_lots:
                if not lot.status:
                    status = ParkingStatus(id=lot.id, filledCount=0)
                    db.session.add(status)
            db.session.commit()
    return render_template('book.html', locations=unique_locations, parking_lots=parking_lots, selected_location=selected_location)

@user_bp.route('/book/confirm', methods=['POST'])
@user_required
def confirm_booking():
    lot_id = request.form.get('lot_id')
    vehicle_number = request.form.get('vehicle_number')
    user_id = session['user_id']
    if not lot_id or not vehicle_number: return "Missing required information!", 400
    lot = ParkingLot.query.get(lot_id)
    if not lot: return "Parking lot not found!", 404
    if not lot.status:
        status = ParkingStatus(id=lot.id, filledCount=0)
        db.session.add(status)
        db.session.commit()
        lot = ParkingLot.query.get(lot_id)
    if lot.status.filledCount >= lot.total_spots: return "No spots available!", 400
    record = ParkingRecord(
        user_id=user_id, vehicle_number=vehicle_number, parking_time=datetime.now(), exit_time=None,
        lot_id=lot.id, price_at_booking=lot.price, lot_location=lot.location, lot_address=lot.address, lot_pin=str(lot.pin)
    )
    db.session.add(record)
    lot.status.filledCount += 1
    db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/exit/<int:record_id>', methods=['GET', 'POST'])
@user_required
def exit_parking(record_id):
    record = ParkingRecord.query.get(record_id)
    if not record or record.user_id != session['user_id']: return "Invalid operation!", 400
    lot = ParkingLot.query.get(record.lot_id)
    if request.method == 'POST':
        if record.exit_time is not None: return "Already exited!", 400
        record.exit_time = datetime.now()
        if lot and lot.status and lot.status.filledCount > 0:
            lot.status.filledCount -= 1
        db.session.commit()
        return redirect(url_for('user.history'))
    end_time = datetime.now()
    start_time = record.parking_time
    hours = ceil((end_time - start_time).total_seconds() / 3600)
    total_amount = hours * record.price_at_booking
    now = end_time
    return render_template('exit.html', record=record, lot=lot, hours=hours, total_amount=total_amount, now=now)

@user_bp.route('/history')
@user_required
def history():
    user = User.query.get(session['user_id'])
    return render_template('history.html', parking_history=user.parking_history)

@user_bp.route('/summary')
@user_required
def summary():
    user = User.query.get(session['user_id'])
    parking_history = user.parking_history
    total_bookings = len(parking_history)
    active_bookings = len([r for r in parking_history if r.exit_time is None])
    completed_bookings = len([r for r in parking_history if r.exit_time is not None])
    location_counts = {}
    for record in parking_history:
        location_name = record.lot.location
        location_counts[location_name] = location_counts.get(location_name, 0) + 1
    most_visited_location = max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else None
    return render_template('summary.html',
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         completed_bookings=completed_bookings,
                         most_visited_location=most_visited_location) 