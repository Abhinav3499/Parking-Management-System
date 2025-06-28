from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import *  # Ensure models.py contains User, ParkingLot, ParkingStatus, etc.
from datetime import datetime
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        if not all([username, password, name, address, pincode]):
            error = "All fields are required!"
        elif not (pincode.isdigit() and len(pincode) == 6):
            error = "Pincode must be a 6-digit number!"
        elif User.query.filter_by(username=username).first():
            error = "User already exists!"
        if not error:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, name=name, address=address, pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['admin'] = user.admin
        if user.admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return "Invalid credentials!", 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ----------------- Admin Routes -----------------

@app.route('/admin')
def admin_dashboard():
    if 'user_id' in session and session.get('admin'):
        users = User.query.all()
        return render_template('adminDashboard.html', users=users)
    return redirect(url_for('index'))

@app.route('/admin/addParkingLot', methods=['GET', 'POST'])
def add_parking_lot():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
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
            new_lot = ParkingLot(
                location=location,
                address=address,
                pin=int(pin),
                total_spots=int(spots),
                price=float(price)
            )
            db.session.add(new_lot)
            db.session.commit()
            new_status = ParkingStatus(id=new_lot.id, filledCount=0)
            db.session.add(new_status)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    return render_template('addParkingLot.html', error=error)

@app.route('/admin/viewParkingLots')
def view_parking_lots():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    parking_lots = ParkingLot.query.all()
    return render_template('viewParkingLots.html', parking_lots=parking_lots)

@app.route('/admin/editParkingLot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return "Parking lot not found!", 404
    error = None
    if request.method == 'POST':
        try:
            new_spots = int(request.form.get('spots'))
            new_price = float(request.form.get('price'))
        except (TypeError, ValueError):
            return "Invalid input!", 400
        occupied = lot.status.filledCount if lot.status else 0
        if new_spots < occupied:
            error = f"Cannot set spots less than currently occupied ({occupied})!"
        else:
            lot.total_spots = new_spots
            lot.price = new_price
            db.session.commit()
            return redirect(url_for('view_parking_lots'))
    return render_template('editParkingLot.html', lot=lot, error=error)

@app.route('/admin/deleteParkingLot/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return "Parking lot not found!", 404
    if lot.status and lot.status.filledCount > 0:
        return "Cannot delete occupied parking lot!", 400
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('view_parking_lots'))

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    users = User.query.filter_by(admin=False).all()
    return render_template('users.html', users=users)

@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    results = None
    if request.method == 'POST':
        location = request.form.get('location')
        pin = request.form.get('pin')
        query = ParkingLot.query
        if location:
            query = query.filter(ParkingLot.location.ilike(f"%{location}%"))
        if pin:
            query = query.filter(ParkingLot.pin == int(pin))
        results = query.all()
    return render_template('search.html', results=results)

# ----------------- User Routes -----------------

@app.route('/user')
def user_dashboard():
    if 'user_id' in session and not session.get('admin'):
        user = User.query.get(session['user_id'])
        return render_template('userDashboard.html', username=session['username'], parking_history=user.parking_history)
    return redirect(url_for('index'))

@app.route('/user/book', methods=['GET', 'POST'])
def book_parking():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
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

@app.route('/user/book/confirm', methods=['POST'])
def confirm_booking():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    lot_id = request.form.get('lot_id')
    vehicle_number = request.form.get('vehicle_number')
    user_id = session['user_id']
    if not lot_id or not vehicle_number:
        return "Missing required information!", 400
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return "Parking lot not found!", 404
    if not lot.status:
        status = ParkingStatus(id=lot.id, filledCount=0)
        db.session.add(status)
        db.session.commit()
        lot = ParkingLot.query.get(lot_id)
    if lot.status.filledCount >= lot.total_spots:
        return "No spots available!", 400
    record = ParkingRecord(
        user_id=user_id,
        vehicle_number=vehicle_number,
        parking_time=datetime.now(),
        exit_time=None,
        lot_id=lot.id,
        price_at_booking=lot.price,
        lot_location=lot.location,
        lot_address=lot.address,
        lot_pin=str(lot.pin)
    )
    db.session.add(record)
    lot.status.filledCount += 1
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/user/exit/<int:record_id>', methods=['GET', 'POST'])
def exit_parking(record_id):
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    record = ParkingRecord.query.get(record_id)
    if not record or record.user_id != session['user_id']:
        return "Invalid operation!", 400
    lot = ParkingLot.query.get(record.lot_id)
    if request.method == 'POST':
        if record.exit_time is not None:
            return "Already exited!", 400
        record.exit_time = datetime.now()
        if lot and lot.status and lot.status.filledCount > 0:
            lot.status.filledCount -= 1
        db.session.commit()
        return redirect(url_for('user_parking_history'))
    # GET: Show details and amount
    end_time = datetime.now()
    start_time = record.parking_time
    hours = ceil((end_time - start_time).total_seconds() / 3600)
    total_amount = hours * record.price_at_booking
    now = end_time
    return render_template('exit.html', record=record, lot=lot, hours=hours, total_amount=total_amount, now=now)

@app.route('/user/history')
def user_parking_history():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    return render_template('history.html', parking_history=user.parking_history)

@app.route('/user/summary')
def user_summary():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    parking_history = user.parking_history
    
    total_bookings = len(parking_history)
    active_bookings = len([r for r in parking_history if r.exit_time is None])
    completed_bookings = len([r for r in parking_history if r.exit_time is not None])
    
    # Find most visited location
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

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if not all([name, address, pincode]):
            error = "All fields are required!"
        elif not (pincode.isdigit() and len(pincode) == 6):
            error = "Pincode must be a 6-digit number!"
        elif old_password and new_password:
            if not check_password_hash(user.password, old_password):
                error = "Old password is incorrect!"
            else:
                user.password = generate_password_hash(new_password)
        if not error:
            user.name = name
            user.address = address
            user.pincode = pincode
            db.session.commit()
            return redirect(url_for('user_dashboard') if not user.admin else url_for('admin_dashboard'))
    return render_template('editProfile.html', user=user, error=error)

# ----------------- Initialize DB with Admin -----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(admin=True).first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                name='Admin',
                admin=True
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
