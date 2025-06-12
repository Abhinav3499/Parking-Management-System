from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # Needed for session

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')

        if not name:
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            return "User already exists!", 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('home'))
    return "Invalid credentials!", 401

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(admin=True).first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                name='Admin',
                admin=True
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
