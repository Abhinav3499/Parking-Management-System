from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    admin = db.Column(db.Boolean, default=False)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class ParkingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=True)
    price_at_booking = db.Column(db.Float, nullable=False)
    lot_location = db.Column(db.String(120), nullable=False)
    lot_address = db.Column(db.String(200), nullable=False)
    lot_pin = db.Column(db.String(20), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('parking_history', lazy=True))
    lot = db.relationship('ParkingLot', backref=db.backref('parking_records', lazy=True))
    spot = db.relationship('ParkingSpot', backref=db.backref('parking_records', lazy=True))

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' for available, 'O' for occupied

    lot = db.relationship('ParkingLot', backref=db.backref('spots', cascade='all, delete-orphan', lazy=True))