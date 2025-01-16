from flask import render_template, request, redirect, url_for, session, flash

from app import app 
from models import User, Quiz, Question, Attempt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime


@app.route('/login')
def login():
    return render_template('login.html')