from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from models.models import db, User, Address
from werkzeug.security import check_password_hash
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token
from utils.oauth_handler import oauth, get_authorization_url, handle_callback
import re
from functools import wraps
from datetime import timedelta

authBp = Blueprint('auth', __name__)

@authBp.route('/', methods=['GET', 'POST'])
def login():
    """Login route supporting both traditional and JWT authentication"""
    if request.method == 'POST':
        inputUsername = request.form.get('username')
        inputPassword = request.form.get('password')
        authenticatedUser = User.query.filter_by(username=inputUsername).first()
        
        if authenticatedUser and authenticatedUser.checkPassword(inputPassword):
            login_user(authenticatedUser)
            
            access_token = create_access_token(
                user_id=authenticatedUser.id,
                is_admin=authenticatedUser.isAdmin
            )
            refresh_token = create_refresh_token(authenticatedUser.id)
            
            response = make_response(redirect(
                url_for('admin.dashboard') if authenticatedUser.isAdmin else url_for('user.dashboard')
            ))
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=timedelta(days=7)
            )
            response.set_cookie('access_token', access_token, max_age=timedelta(hours=1))
            
            return response
        else:
            flash('Invalid username or password', 'error')
    return render_template('index.html')

@authBp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route supporting both traditional and JWT authentication"""
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
        
        newUser = User(
            username=newUsername,
            name=newUserName,
            addressId=userAddress.id,
            isAdmin=False
        )
        newUser.setPassword(newPassword)
        db.session.add(newUser)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@authBp.route('/auth/google')
def google_login():
    """Redirect to Google OAuth login"""
    return get_authorization_url()

@authBp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        user_info = handle_callback(request.url)
    except Exception as e:
        print(f"OAuth callback error: {e}")
        flash('Failed to authenticate with Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user_info:
        flash('Failed to authenticate with Google', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(google_id=user_info['google_id']).first()
    
    if not user:
        user = User.query.filter_by(username=user_info['email']).first()
        
        if user:
            user.google_id = user_info['google_id']
            user.profile_picture = user_info.get('picture')
        else:
            user = User(
                username=user_info['email'],
                name=user_info['name'],
                google_id=user_info['google_id'],
                profile_picture=user_info.get('picture'),
                isAdmin=False
            )
            db.session.add(user)
        
        db.session.commit()
    
    login_user(user)
    
    access_token = create_access_token(
        user_id=user.id,
        is_admin=user.isAdmin
    )
    refresh_token = create_refresh_token(user.id)
    
    response = make_response(redirect(
        url_for('admin.dashboard') if user.isAdmin else url_for('user.dashboard')
    ))
    
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=timedelta(days=7)
    )
    response.set_cookie('access_token', access_token, max_age=timedelta(hours=1))
    
    return response

@authBp.route('/auth/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token"""
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'No refresh token provided'}), 401
    
    payload = verify_token(refresh_token, 'refresh')
    
    if not payload:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401
    
    user = User.query.get(payload['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    new_access_token = create_access_token(
        user_id=user.id,
        is_admin=user.isAdmin
    )
    
    return jsonify({'access_token': new_access_token}), 200

@authBp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout route - clears session and tokens"""
    logout_user()
    
    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    
    return response

def adminRequired(fn):
    """Decorator for admin-only routes (Flask-Login based)"""
    @wraps(fn)
    def decoratedView(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.isAdmin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return decoratedView