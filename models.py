from app import app 
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy(app)

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
    id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), primary_key=True)
    location = db.Column(db.String(120), unique=True, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    pin = db.Column(db.Integer, nullable=False)
    
    parking_lot = db.relationship('ParkingLot', backref=db.backref('parking_lots', lazy=True))

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        password_hash = generate_password_hash('admin')
        admin = User(username='admin', password=password_hash, name='Admin', admin=True)
        db.session.add(admin)
        db.session.commit()