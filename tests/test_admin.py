import pytest
from app import create_app, db
from app.logging import get_event
from unittest.mock import patch

def test_admin_route_no_permission(client):
    """Test the admin route without admin permissions."""
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    print(response.data.decode())
    assert b"have admin permissions" in response.data

def test_admin_route(client, create_user):
    """Test the admin route."""
    client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data or b'Admin Page' in response.data

@patch('app.admin.get_event')
def test_admin_see_logs(mocked_get_event, client, create_user):
    client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    mocked_get_event.return_value = [('123', 'msg_type_all' ,'random event')]

    response = client.post('/logs', follow_redirects = True)
    assert response.status_code == 200
    assert mocked_get_event.call_count == 1
    assert b'random event' in response.data
    
@patch('app.admin.requests.post')
def test_set_threshold(mocked_post, client, create_user):
    client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    mock_response = mocked_post.return_value
    mock_response.status_code = 200
    mocked_post.status_code = 200
    data = {
        'threshold': 70
    }

    response = client.post('/set_threshold', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_post.call_count == 1
    assert b'Success' in response.data

@patch('app.admin.requests.post')
def test_set_threshold_failed(mocked_post, client, create_user):
    client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    mock_response = mocked_post.return_value
    mock_response.status_code = 404
    mocked_post.status_code = 404
    data = {
        'threshold': 70
    }

    response = client.post('/set_threshold', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_post.call_count == 1
    assert b'Setting threshold failed' in response.data


def test_set_threshold_access_denied(client, create_user):
    with client.session_transaction() as sess:
        sess['is_admin'] = False

    response = client.post('/set_threshold', content_type='multipart/form-data', follow_redirects = True)
    assert response.status_code == 200
    assert b'have permissions to do that' in response.data