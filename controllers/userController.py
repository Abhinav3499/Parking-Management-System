from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User, ParkingLot, ParkingRecord, ParkingSpot, Address
from datetime import datetime 
import math
import qrcode
import io
import base64 
import re

userBp = Blueprint('user', __name__, url_prefix='/user')

@userBp.before_request
@login_required
def beforeRequest():
    pass

def createParkingBooking(selectedLot, userVehicleNumber, currentUserId):
    # Validate vehicle number
    if not re.match(r'^[A-Za-z0-9]{4,15}$', userVehicleNumber):
        return None, 'Vehicle number must be 4-15 alphanumeric characters'

    availableSpot = ParkingSpot.query.filter_by(lotId=selectedLot.id, status='A').order_by(ParkingSpot.spotNumber).first()

    if not availableSpot:
        return None, 'No available spots in this parking lot'

    availableSpot.status = 'O'
    newParkingRecord = ParkingRecord(
        userId=currentUserId,
        vehicleNumber=userVehicleNumber,
        lotId=selectedLot.id,
        entryTime=datetime.utcnow(), 
        bookingPrice=selectedLot.pricePerHour,
        lotLocation=selectedLot.location,
        lotAddress=selectedLot.address.address,
        lotPincode=selectedLot.address.pincode,
        spotId=availableSpot.id
    )

    db.session.add(newParkingRecord)
    db.session.commit()
    
    return newParkingRecord, None

@userBp.route('/')
def dashboard():
    activeBookings = ParkingRecord.query.filter_by(userId=current_user.id, exitTime=None).all()
    
    return render_template('userDashboard.html', 
                         user=current_user,
                         activeBookings=activeBookings)

@userBp.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        selectedLotId = request.form.get('lotId')
        userVehicleNumber = request.form.get('vehicleNumber')
        selectedLot = ParkingLot.query.get(selectedLotId)

        if not selectedLot:
            flash('Invalid parking lot selected', 'error')
            return redirect(url_for('user.book'))

        newParkingRecord, errorMessage = createParkingBooking(selectedLot, userVehicleNumber, current_user.id)
        
        if errorMessage:
            flash(errorMessage, 'error')
            return redirect(url_for('user.book'))

        return redirect(url_for('user.summary', recordId=newParkingRecord.id))

    searchLocation = request.args.get('searchLocation', '')
    searchPincode = request.args.get('searchPin', '')
    
    # Backend validation for pincode
    if searchPincode and (not searchPincode.isdigit() or len(searchPincode) != 6):
        flash('Pincode must be 6 digits', 'error')
        searchPincode = ''
    
    lotQuery = ParkingLot.query 
    if searchLocation:
        lotQuery = lotQuery.filter(ParkingLot.location.ilike(f'%{searchLocation}%'))
    if searchPincode:
        lotQuery = lotQuery.join(Address).filter(Address.pincode.ilike(f'%{searchPincode}%'))
    
    availableLots = lotQuery.all()

    return render_template('book.html', parkingLots=availableLots, searchLocation=searchLocation, searchPin=searchPincode)

@userBp.route('/book-lot/<int:lotId>', methods=['GET', 'POST'])
def bookLot(lotId):
    selectedLot = ParkingLot.query.get_or_404(lotId)
    
    if request.method == 'POST':
        userVehicleNumber = request.form.get('vehicleNumber')

        newParkingRecord, errorMessage = createParkingBooking(selectedLot, userVehicleNumber, current_user.id)
        
        if errorMessage:
            flash(errorMessage, 'error')
            return redirect(url_for('user.book'))

        return redirect(url_for('user.summary', recordId=newParkingRecord.id))

    return render_template('bookLot.html', lot=selectedLot)

@userBp.route('/bookingSummary/<int:recordId>')
def summary(recordId):
    parkingRecord = ParkingRecord.query.get(recordId)
    if not parkingRecord:
        return "Record not found", 404

    return render_template('bookingSummary.html', record=parkingRecord)

@userBp.route('/exit/<int:recordId>', methods=['GET', 'POST'])
def exit(recordId):
    parkingRecord = ParkingRecord.query.get(recordId)
    if not parkingRecord:
        return "Record not found", 404

    if request.method == 'POST':
        currentExitTime = datetime.utcnow()
        parkingRecord.exitTime = currentExitTime
        parkingRecord.parkingSpot.status = 'A'
        
        totalHours = math.ceil((currentExitTime - parkingRecord.entryTime).total_seconds() / 3600)
        calculatedAmount = totalHours * parkingRecord.bookingPrice
        parkingRecord.totalAmountPaid = calculatedAmount
        
        db.session.commit()

        return redirect(url_for('user.paymentQR', recordId=parkingRecord.id))
    
    currentExitTime = datetime.utcnow()
    totalHours = math.ceil((currentExitTime - parkingRecord.entryTime).total_seconds() / 3600)
    calculatedAmount = totalHours * parkingRecord.bookingPrice

    return render_template('exit.html', record=parkingRecord, hours=totalHours, amount=calculatedAmount)

@userBp.route('/payment-qr/<int:recordId>')
def paymentQR(recordId):
    parkingRecord = ParkingRecord.query.get(recordId)
    if not parkingRecord:
        return "Record not found", 404
    
    calculatedAmount = parkingRecord.totalAmountPaid
    
    upiPaymentString = f"upi://pay?pa=abhinavarya@oksbi&pn=Parking%20Payment&am={calculatedAmount}&cu=INR"
    
    qrCodeGenerator = qrcode.QRCode(version=1, box_size=10, border=5)
    qrCodeGenerator.add_data(upiPaymentString)
    qrCodeGenerator.make(fit=True)
    
    qrCodeImage = qrCodeGenerator.make_image(fill_color="black", back_color="white")
    
    imageBuffer = io.BytesIO()
    qrCodeImage.save(imageBuffer, format='PNG')
    qrCodeBase64 = base64.b64encode(imageBuffer.getvalue()).decode()
    
    return render_template('paymentQR.html', record=parkingRecord, amount=calculatedAmount, qr_code=qrCodeBase64)

@userBp.route('/record')
def record():
    return render_template('record.html', history=current_user.parkingRecords)

@userBp.route('/edit-profile', methods=['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        updatedName = request.form.get('name')
        updatedAddress = request.form.get('address')
        updatedPincode = request.form.get('pincode')
        newUserPassword = request.form.get('new_password')
        confirmNewPassword = request.form.get('confirm_password')
        
        if not updatedName or not updatedAddress or not updatedPincode:
            flash('All fields are required', 'error')
            return render_template('userEditProfile.html', user=current_user)
        
        if not updatedPincode.isdigit() or len(updatedPincode) != 6:
            flash('Pincode must be 6 digits', 'error')
            return render_template('userEditProfile.html', user=current_user)
        
        if newUserPassword:
            if len(newUserPassword) < 8:
                flash('Password must be at least 8 characters long', 'error')
                return render_template('userEditProfile.html', user=current_user)
                
            if newUserPassword != confirmNewPassword:
                flash('Passwords do not match', 'error')
                return render_template('userEditProfile.html', user=current_user)

            current_user.setPassword(newUserPassword)

        current_user.name = updatedName

        if current_user.address:
            current_user.address.address = updatedAddress
            current_user.address.pincode = updatedPincode
        else:
            newAddressForUser = Address(address=updatedAddress, pincode=updatedPincode)
            db.session.add(newAddressForUser)
            db.session.commit()
            current_user.addressId = newAddressForUser.id
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('userEditProfile.html', user=current_user)
