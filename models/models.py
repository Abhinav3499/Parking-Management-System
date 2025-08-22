from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passwordHash = db.Column("password", db.String(256), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    addressId = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    isAdmin = db.Column("admin", db.Boolean, default=False)

    address = db.relationship('Address', backref=db.backref('users', lazy=True))

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash, password)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    addressId = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    totalSpots = db.Column(db.Integer, nullable=False)
    pricePerHour = db.Column("price", db.Integer, nullable=False)

    address = db.relationship('Address', backref=db.backref('parkingLots', lazy=True))

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lotId = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spotNumber = db.Column(db.Integer, nullable=False) 
    status = db.Column(db.String(1), nullable=False, default='A') 

    parkingLot = db.relationship('ParkingLot', backref=db.backref('parkingSpots', cascade='all, delete-orphan', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('lotId', 'spotNumber', name='_lot_spot_uc'),)


class ParkingRecord(db.Model):
    __tablename__ = 'parking_record'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicleNumber = db.Column(db.String(15), nullable=False)
    entryTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exitTime = db.Column(db.DateTime, nullable=True)

    lotId = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=True)
    spotId = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)
    bookingPrice = db.Column(db.Integer, nullable=False)
    totalAmountPaid = db.Column(db.Integer, nullable=True, default=0)

    lotLocation = db.Column(db.String(100), nullable=False)
    lotAddress = db.Column(db.String(100), nullable=False)
    lotPincode = db.Column("lotPin", db.String(6), nullable=False)

    user = db.relationship('User', backref=db.backref('parkingRecords', lazy=True))
    parkingLot = db.relationship('ParkingLot', backref=db.backref('parkingRecords', lazy=True))
    parkingSpot = db.relationship('ParkingSpot', backref=db.backref('parkingRecords', lazy=True))
