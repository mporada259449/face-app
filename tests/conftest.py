from app.config import TestConfig
from app.models import db
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