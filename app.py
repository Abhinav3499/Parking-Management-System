from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize app and extensions
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Initialize migrations
migrate = Migrate(app, db)

# Import blueprints
from auth import auth_blueprint
from views import views_blueprint

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(views_blueprint, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)
