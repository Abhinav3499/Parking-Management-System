from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.models import db, User, Address
from werkzeug.security import check_password_hash
import re
from functools import wraps

authBp = Blueprint('auth', __name__)

@authBp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        inputUsername = request.form.get('username')
        inputPassword = request.form.get('password')
        authenticatedUser = User.query.filter_by(username=inputUsername).first()
        if authenticatedUser and authenticatedUser.checkPassword(inputPassword):
            login_user(authenticatedUser)
            if authenticatedUser.isAdmin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('index.html')

@authBp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        newUsername = request.form.get('username')
        newPassword = request.form.get('password')
        newUserName = request.form.get('name')
        newUserAddress = request.form.get('address')
        newUserPincode = request.form.get('pincode')

        if not re.match(r'[^@]+@[^@]+\.[^@]+', newUsername):
            flash('Invalid email address', 'error')
            return render_template('register.html', **request.form)
        
        if len(newPassword) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('register.html', **request.form)

        if not newUserPincode.isdigit() or len(newUserPincode) != 6:
            flash('Pincode must be 6 digits', 'error')
            return render_template('register.html', **request.form)

        if User.query.filter_by(username=newUsername).first():
            flash('Username already exists', 'error')
            return render_template('register.html', **request.form)
            
        userAddress = Address(address=newUserAddress, pincode=newUserPincode)
        db.session.add(userAddress)
        db.session.commit()
        newUser = User(username=newUsername, name=newUserName, addressId=userAddress.id, isAdmin=False)
        newUser.setPassword(newPassword)
        db.session.add(newUser)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@authBp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 

def adminRequired(fn):
    @wraps(fn)
    def decoratedView(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.isAdmin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return decoratedView