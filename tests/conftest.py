import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

def test_app_context(app):
    """Test the app context setup and teardown."""
    with app.app_context():
        assert db.engine.url.database == TestConfig.SQLALCHEMY_DATABASE_URI

def test_client_context(client):
    """Test the client context setup."""
    response = client.get('/')
    assert response.status_code == 404  # Assuming the root route is not defined