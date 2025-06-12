from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, default=False)

class ParkingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(120), nullable=False)

    user = db.relationship('User', backref=db.backref('parking_history', lazy=True))

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), unique=True, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    pin = db.Column(db.Integer, nullable=False)
