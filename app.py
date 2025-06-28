from flask import Flask, url_for, redirect
from models import db, User
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'supersecretkey'

    db.init_app(app)

    from controllers.auth_controllers import auth_bp
    from controllers.admin_controllers import admin_bp
    from controllers.user_controllers import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(admin=True).first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                name='Admin',
                address='N/A',
                pincode='000000',
                admin=True
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
