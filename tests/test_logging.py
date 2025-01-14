import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

def test_logging_setup(client):
    """Test the logging setup."""
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Check for a specific element or text in the HTML content

def test_logging_setup(app):
    """Test the logging setup."""
    with app.app_context():
        assert app.logger is not None
        app.logger.info('Test log message')