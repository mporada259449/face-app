import os

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASS')}@{os.getenv('DATABASE_ADRESS')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    CSRF_ENABLED = False