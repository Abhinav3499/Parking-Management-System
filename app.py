from flask import Flask
from flask_login import LoginManager
from models.models import db, User, Address
from controllers.authController import authBp
from controllers.userController import userBp
from controllers.adminController import adminBp
from utils.oauth_handler import init_oauth
from config import DevelopmentConfig, ProductionConfig
import os

def createApp():
    app = Flask(__name__)
    
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Session configuration for OAuth
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

    db.init_app(app)
    
    init_oauth(app)

    loginManager = LoginManager()
    loginManager.init_app(app)
    loginManager.login_view = 'auth.login'

    @loginManager.user_loader
    def loadUser(userId):
        return User.query.get(int(userId))

    app.register_blueprint(authBp)
    app.register_blueprint(userBp)
    app.register_blueprint(adminBp)

    return app

if __name__ == '__main__':
    app = createApp()
    
    # Ensure instance directory exists
    import os
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(isAdmin=True).first():
            adminAddress = Address(address='Admin Address', pincode='000000')
            db.session.add(adminAddress)
            db.session.commit()
            adminUser = User(
                username='admin',
                name='Admin',
                addressId=adminAddress.id,
                isAdmin=True
            )
            adminUser.setPassword('admin')
            db.session.add(adminUser)
            db.session.commit()
    app.run(debug=True)
     
