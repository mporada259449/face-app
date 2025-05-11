import pytest
from app import create_app, db

def test_login_route(client, create_user):
    """Test the login route."""
    response = client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_login_failure(client, create_user):
    response = client.post('/login', data={'username': 'admin', 'password': 'worngpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid password or login' in response.data

def test_login_no_data(client, create_user):
    response = client.post('/login', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_logout_user(client, create_user):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_admin'] = True
        sess['username'] = 'admin'

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out" in response.data

    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'is_admin' not in sess
        assert 'username' not in sess