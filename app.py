from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import *  # Ensure models.py contains User, ParkingLot, ParkingStatus, etc.
from datetime import datetime

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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')

        if not name:
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            return "User already exists!", 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')

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

@app.route('/admin/addLocation', methods=['GET', 'POST'])
def add_location():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        pin = request.form.get('pin')
        if not all([name, address, pin]):
            return "All fields are required!", 400
        new_location = Location(name=name, address=address, pin=int(pin))
        db.session.add(new_location)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('addLocation.html')

@app.route('/admin/addParkingLot', methods=['GET', 'POST'])
def add_parking_lot():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        location_name = request.form.get('location_name')
        total_spots = request.form.get('spot')
        price = request.form.get('price')
        if not all([location_name, total_spots, price]):
            return "All fields are required!", 400
        # Find or create location by name (using default address and pin if not found)
        location = Location.query.filter_by(name=location_name).first()
        if not location:
            location = Location(name=location_name, address='Default Address', pin=0)
            db.session.add(location)
            db.session.commit()
        new_lot = ParkingLot(
            location_id=location.id,
            total_spots=int(total_spots),
            price=float(price)
        )
        new_lot.status = ParkingStatus(filledCount=0)
        db.session.add(new_lot)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('addParkingLot.html')

@app.route('/admin/viewParkingLots')
def view_parking_lots():
    if 'user_id' not in session or not session.get('admin'):
        return redirect(url_for('index'))
    locations = Location.query.all()
    return render_template('viewParkingLots.html', locations=locations)

# ----------------- User Routes -----------------

@app.route('/user')
def user_dashboard():
    if 'user_id' in session and not session.get('admin'):
        user = User.query.get(session['user_id'])
        return render_template('userDashboard.html', username=session['username'], parking_history=user.parking_history)
    return redirect(url_for('index'))

# @app.route('/user/book', methods=['POST', 'GET'])
# def book_parking():
#     if 'user_id' not in session or session.get('admin'):
#         return redirect(url_for('index'))
#     # Booking logic would go here
#     return redirect(url_for('user_dashboard'))

# @app.route('/user/view')
# def view_parking_history():
#     if 'user_id' not in session or session.get('admin'):
#         return redirect(url_for('index'))
#     user = User.query.get(session['user_id'])
#     return render_template('viewParkingHistory.html', parking_history=user.parking_history)

@app.route('/user/book', methods=['POST', 'GET'])
def book_parking():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    locations = Location.query.all()
    parking_lots = ParkingLot.query.all()
    if request.method == 'POST':
        location_id = request.form.get('location_id')
        if location_id:
            lots = ParkingLot.query.filter_by(location_id=location_id).all()
            return render_template('searchResult.html', parking_lots=lots)
    return render_template('book.html', locations=locations, parking_lots=parking_lots)

@app.route('/user/book/confirm', methods=['POST'])
def confirm_booking():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    lot_id = request.form.get('lot_id')
    vehicle_number = request.form.get('vehicle_number')
    user_id = session['user_id']
    lot = ParkingLot.query.get(lot_id)
    status = ParkingStatus.query.get(lot_id)
    if status.filledCount >= lot.total_spots:
        return "No spots available!", 400
    # Find location
    location = lot.location
    # Create booking record
    record = ParkingRecord(
        user_id=user_id,
        vehicle_number=vehicle_number,
        parking_time=datetime.now(),
        exit_time=None,
        location_id=location.id
    )
    db.session.add(record)
    status.filledCount += 1
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/user/exit/<int:record_id>', methods=['POST'])
def exit_parking(record_id):
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    record = ParkingRecord.query.get(record_id)
    if not record or record.user_id != session['user_id'] or record.exit_time is not None:
        return "Invalid operation!", 400
    record.exit_time = datetime.now()
    # Decrement filledCount for the lot
    lot = ParkingLot.query.filter_by(location_id=record.location_id).first()
    if lot:
        status = ParkingStatus.query.get(lot.id)
        if status and status.filledCount > 0:
            status.filledCount -= 1
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/user/history')
def user_parking_history():
    if 'user_id' not in session or session.get('admin'):
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    return render_template('history.html', parking_history=user.parking_history)

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
