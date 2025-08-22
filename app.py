from flask import Flask
from flask_login import LoginManager
from models.models import db, User, Address
from controllers.authController import authBp
from controllers.userController import userBp
from controllers.adminController import adminBp


def createApp():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'AbhianvArya'

    db.init_app(app)

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
