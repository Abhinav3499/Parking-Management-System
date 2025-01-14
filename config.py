class Config:
    SECRET_KEY = 'mysecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz_app.db'  # Database file
    SQLALCHEMY_TRACK_MODIFICATIONS = False