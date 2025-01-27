from flask import render_template, request, redirect, url_for, session, flash

from app import app 
from models import User, Quiz, Question, Attempt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')