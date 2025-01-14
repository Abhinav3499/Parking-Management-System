from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import db, create_default_admin

# Initialize app and extensions
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Import blueprints
from auth import auth_blueprint
from views import views_blueprint

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(views_blueprint, url_prefix='/')

# Create the database and the default admin user
with app.app_context():
    db.create_all()  # Create database tables
    create_default_admin()  # Create default admin user

if __name__ == "__main__":
    app.run(debug=True)