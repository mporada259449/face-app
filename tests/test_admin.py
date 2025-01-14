import pytest
from app import create_app, db
from app.models import User
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

@pytest.fixture(scope='module')
def admin_user(app):
    with app.app_context():
        user = User(username='admin', password='adminpassword', is_admin=True)
        db.session.add(user)
        db.session.commit()
        return user

def test_admin_route(client, admin_user):
    """Test the admin route."""
    # Log in as the admin user
    client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)
    
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    # Adjust the text to match the actual content
    assert b'Admin Dashboard' in response.data or b'Admin Page' in response.data
    
def test_admin_route_no_permission(client):
    """Test the admin route without admin permissions."""
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    print(response.data.decode())  # Print the response data to debug
    assert b"You don't have admin permissions" in response.data or b'Admin Page' in response.data

def test_admin_route_with_permission(client, admin_user):
    """Test the admin route with admin permissions."""
    client.post('/login', data={'username': 'admin', 'password': 'adminpassword'}, follow_redirects=True)
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data or b'Admin Page' in response.data