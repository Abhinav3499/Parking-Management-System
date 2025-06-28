from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        if not all([username, password, name, address, pincode]):
            error = "All fields are required!"
        elif not (pincode.isdigit() and len(pincode) == 6):
            error = "Pincode must be a 6-digit number!"
        elif User.query.filter_by(username=username).first():
            error = "User already exists!"
        if not error:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, name=name, address=address, pincode=pincode)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('register.html', error=error)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['admin'] = user.admin
            if user.admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        return "Invalid credentials!", 401
    return render_template('index.html') # The main page is the login page

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if not all([name, address, pincode]):
            error = "All fields are required!"
        elif not (pincode.isdigit() and len(pincode) == 6):
            error = "Pincode must be a 6-digit number!"
        elif old_password and new_password:
            if not check_password_hash(user.password, old_password):
                error = "Old password is incorrect!"
            else:
                user.password = generate_password_hash(new_password)
        if not error:
            user.name = name
            user.address = address
            user.pincode = pincode
            db.session.commit()
            if user.admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
    return render_template('editProfile.html', user=user, error=error) 