from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    attempts = db.relationship('Attempt', backref='user', lazy=True)

class Quiz(db.Model):
    quiz_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    chapter = db.Column(db.String(255), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    attempts = db.relationship('Attempt', backref='quiz', lazy=True)

class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)  # 
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(1), nullable=False)  # 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    attempts = db.relationship('Attempt', backref='question', lazy=True)

class Attempt(db.Model):
    attempt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable=False)
    choice = db.Column(db.String(1), nullable=False)  # 
    is_correct = db.Column(db.Boolean, default=False)
