from flask import session
from app.config import TestConfig
from app.models import db, User
from app import create_app
import pytest

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    with app.app_context():
        return app.test_client()

@pytest.fixture
def db_session():
    yield db.session
    
@pytest.fixture
def create_admin(db_session):
    admin = User(id = 1, username = 'admin', password = 'password', is_admin='True')
    db_session.add(admin)
    yield admin

@pytest.fixture
def admin_login(create_admin):
    session['user_id'] = 'admin'
    session['is_admin'] = True
    yield
    session.pop('is_admin')
    session.pop('user_id')