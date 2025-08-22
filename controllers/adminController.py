from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User, ParkingLot, ParkingRecord, ParkingSpot, Address
from controllers.authController import adminRequired
import re

adminBp = Blueprint('admin', __name__, url_prefix='/admin')

@adminBp.before_request
@login_required
@adminRequired
def beforeRequest():
    pass

@adminBp.route('/')
def dashboard():
    allParkingLots = ParkingLot.query.all()
    return render_template('adminDashboard.html', parkingLots=allParkingLots)

@adminBp.route('/add-parking-lot', methods=['GET', 'POST'])
def addParkingLot():
    if request.method == 'POST':
        newLocation = request.form.get('location')
        newAddress = request.form.get('address')
        newPincode = request.form.get('pincode')
        newTotalSpots = request.form.get('spots')
        newPricePerHour = request.form.get('price')

        # Backend validation
        if not newPincode.isdigit() or len(newPincode) != 6:
            flash('Pincode must be 6 digits', 'error')
            return render_template('addParkingLot.html', **request.form)
        
        try:
            spots_int = int(newTotalSpots)
            if spots_int <= 0 or spots_int > 1000:
                flash('Number of spots must be between 1 and 1000', 'error')
                return render_template('addParkingLot.html', **request.form)
        except (ValueError, TypeError):
            flash('Number of spots must be a valid number', 'error')
            return render_template('addParkingLot.html', **request.form)
        
        try:
            price_float = float(newPricePerHour)
            if price_float < 0 or price_float > 10000:
                flash('Price per hour must be between 0 and 10000', 'error')
                return render_template('addParkingLot.html', **request.form)
        except (ValueError, TypeError):
            flash('Price per hour must be a valid number', 'error')
            return render_template('addParkingLot.html', **request.form)

        lotAddress = Address(address=newAddress, pincode=newPincode)
        db.session.add(lotAddress)
        db.session.commit()

        newParkingLot = ParkingLot(
            location=newLocation,
            addressId=lotAddress.id,
            totalSpots=spots_int,
            pricePerHour=price_float
        )
        db.session.add(newParkingLot)
        db.session.commit()

        for spotIndex in range(1, spots_int + 1):
            newSpot = ParkingSpot(
                lotId=newParkingLot.id,
                spotNumber=spotIndex,
                status='A'
            )
            db.session.add(newSpot)
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('addParkingLot.html')

@adminBp.route('/edit-parking-lot/<int:lotId>', methods=['GET', 'POST'])
def editParkingLot(lotId):
    selectedParkingLot = ParkingLot.query.get_or_404(lotId)
    if request.method == 'POST':
        newLocation = request.form.get('location')
        newAddress = request.form.get('address')
        newPincode = request.form.get('pincode')
        newTotalSpots = request.form.get('spots')
        newPricePerHour = request.form.get('price')

        # Backend validation
        if not newPincode.isdigit() or len(newPincode) != 6:
            flash('Pincode must be 6 digits', 'error')
            return render_template('editParkingLot.html', lot=selectedParkingLot)
        
        try:
            updatedTotalSpots = int(newTotalSpots)
            if updatedTotalSpots <= 0 or updatedTotalSpots > 1000:
                flash('Number of spots must be between 1 and 1000', 'error')
                return render_template('editParkingLot.html', lot=selectedParkingLot)
        except (ValueError, TypeError):
            flash('Number of spots must be a valid number', 'error')
            return render_template('editParkingLot.html', lot=selectedParkingLot)
        
        try:
            price_float = float(newPricePerHour)
            if price_float < 0 or price_float > 10000:
                flash('Price per hour must be between 0 and 10000', 'error')
                return render_template('editParkingLot.html', lot=selectedParkingLot)
        except (ValueError, TypeError):
            flash('Price per hour must be a valid number', 'error')
            return render_template('editParkingLot.html', lot=selectedParkingLot)

        selectedParkingLot.location = newLocation
        selectedParkingLot.address.address = newAddress
        selectedParkingLot.address.pincode = newPincode
        selectedParkingLot.pricePerHour = price_float

        currentTotalSpots = selectedParkingLot.totalSpots
        actualSpotCount = ParkingSpot.query.filter_by(lotId=lotId).count()
        currentOccupiedSpots = ParkingSpot.query.filter_by(lotId=lotId, status='O').count()

        if currentOccupiedSpots > updatedTotalSpots:
            flash('Cannot reduce spots below occupied spots count', 'error')
            return render_template('editParkingLot.html', lot=selectedParkingLot)
        elif updatedTotalSpots > actualSpotCount:
            
            maxSpotNumber = db.session.query(db.func.max(ParkingSpot.spotNumber)).filter_by(lotId=lotId).scalar() or 0
            spotsToAdd = updatedTotalSpots - actualSpotCount
            
            for i in range(spotsToAdd):
                newSpot = ParkingSpot(
                    lotId=lotId,
                    spotNumber=maxSpotNumber + 1 + i,
                    status='A'
                )
                db.session.add(newSpot)
        elif updatedTotalSpots < actualSpotCount:
            spotsToDeleteCount = actualSpotCount - updatedTotalSpots
            availableSpotsToDelete = ParkingSpot.query.filter_by(lotId=lotId, status='A').order_by(ParkingSpot.spotNumber.desc()).limit(spotsToDeleteCount).all()
            for spotToDelete in availableSpotsToDelete:
                db.session.delete(spotToDelete)
        selectedParkingLot.totalSpots = updatedTotalSpots
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('editParkingLot.html', lot=selectedParkingLot)

@adminBp.route('/delete-parking-lot/<int:lotId>', methods=['POST'])
def deleteParkingLot(lotId):
    selectedParkingLot = ParkingLot.query.get_or_404(lotId)

    currentOccupiedSpots = ParkingSpot.query.filter_by(lotId=selectedParkingLot.id, status='O').count()
    if currentOccupiedSpots > 0:
        flash('Cannot delete lot with occupied spots', 'error')
        return redirect(url_for('admin.dashboard'))
    
    ParkingRecord.query.filter_by(lotId=lotId).update({'lotId': None})
    spotsToDelete = [spot.id for spot in ParkingSpot.query.filter_by(lotId=lotId).all()]
    if spotsToDelete:
        ParkingRecord.query.filter(ParkingRecord.spotId.in_(spotsToDelete)).update({'spotId': None}, synchronize_session=False)
    ParkingSpot.query.filter_by(lotId=lotId).delete()
    db.session.delete(selectedParkingLot)
    db.session.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@adminBp.route('/users')
def manageUsers():
    allNonAdminUsers = User.query.filter_by(isAdmin=False).all()
    return render_template('users.html', users=allNonAdminUsers)

@adminBp.route('/search', methods=['GET', 'POST'])
def search():
    searchResults = None 
    if request.method == 'POST':
        searchLocation = request.form.get('location')
        searchPincode = request.form.get('pincode')
        
        # Backend validation for pincode
        if searchPincode and (not searchPincode.isdigit() or len(searchPincode) != 6):
            flash('Pincode must be 6 digits', 'error')
            return render_template('search.html', results=searchResults)
        
        searchQuery = ParkingLot.query
        if searchLocation:
            searchQuery = searchQuery.filter(ParkingLot.location.ilike(f'%{searchLocation}%'))
        if searchPincode:
            searchQuery = searchQuery.join(Address).filter(Address.pincode == searchPincode)

        searchResults = searchQuery.all()
    return render_template('search.html', results=searchResults)

@adminBp.route('/delete-spot/<int:spotId>', methods=['POST'])
def deleteSpot(spotId):
    selectedSpot = ParkingSpot.query.get_or_404(spotId)
    if selectedSpot.status == 'O':
        flash('Cannot delete occupied spot', 'error')
        return redirect(url_for('admin.dashboard'))
        
    associatedParkingLot = ParkingLot.query.get(selectedSpot.lotId)
    ParkingRecord.query.filter_by(spotId=selectedSpot.id).update({'spotId': None})
    db.session.delete(selectedSpot)
    
    if associatedParkingLot:
        actualSpotCount = ParkingSpot.query.filter_by(lotId=associatedParkingLot.id).count()
        associatedParkingLot.totalSpots = actualSpotCount
    
    db.session.commit()
    flash('Spot deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@adminBp.route('/spot-details/<int:spotId>')
def spotDetails(spotId):
    selectedSpot = ParkingSpot.query.get_or_404(spotId)
    activeParkingRecord = None 
    if selectedSpot.status == 'O':
        activeParkingRecord = ParkingRecord.query.filter_by(spotId=selectedSpot.id, exitTime=None).first()
    return render_template('spotDetails.html', spot=selectedSpot, record=activeParkingRecord)

@adminBp.route('/summary')
def summary():
    totalParkingLots = ParkingLot.query.count()
    totalParkingSpots = db.session.query(db.func.sum(ParkingLot.totalSpots)).scalar() or 0
    totalOccupiedSpots = ParkingSpot.query.filter_by(status='O').count()
    totalAvailableSpots = totalParkingSpots - totalOccupiedSpots
    totalRegisteredUsers = User.query.filter_by(isAdmin=False).count()
    
    adminSummaryData = {
        'totalLots': totalParkingLots,
        'totalSpots': totalParkingSpots,
        'occupiedSpots': totalOccupiedSpots,
        'availableSpots': totalAvailableSpots,
        'totalUsers': totalRegisteredUsers
    }
    
    return render_template('summary.html', summary=adminSummaryData)

@adminBp.route('/edit-profile', methods=['GET', 'POST'])
def editProfile():
    currentAdminUser = User.query.get(current_user.id)
    if request.method == 'POST':
        newName = request.form.get('name')
        newAddress = request.form.get('address')
        newPincode = request.form.get('pincode')
        newAdminPassword = request.form.get('new_password')

        # Backend validation
        if not newPincode.isdigit() or len(newPincode) != 6:
            flash('Pincode must be 6 digits', 'error')
            return render_template('editProfile.html', user=currentAdminUser)
        
        if newAdminPassword and len(newAdminPassword) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('editProfile.html', user=currentAdminUser)

        currentAdminUser.name = newName
        currentAdminUser.address.address = newAddress
        currentAdminUser.address.pincode = newPincode
        
        if newAdminPassword:
            currentAdminUser.setPassword(newAdminPassword)
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('editProfile.html', user=currentAdminUser) 

