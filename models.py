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
    status = db.relationship(
        'ParkingStatus',
        backref='parking_lot',
        uselist=False,
        cascade="all, delete-orphan"
    )

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

    user = db.relationship('User', backref=db.backref('parking_history', lazy=True))
    lot = db.relationship('ParkingLot', backref=db.backref('parking_records', lazy=True))

class ParkingStatus(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), primary_key=True)
    filledCount = db.Column(db.Integer, nullable=False)