import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    app.config['SECRET_KEY'] = 'test_secret_key'  # Ensure the secret key is set
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

def test_login_route(client):
    """Test the login route."""
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Check for a specific element or text in the HTML content

def test_register_route(client):
    """Test the register route."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_register_user(client):
    """Test registering a new user."""
    response = client.post('/register', data={'username': 'newuser', 'password': 'newpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'User registered successfully' in response.data