from unittest.mock import patch, MagicMock
from io import BytesIO
from app.views import allowed_file, send_compare_request
from app.logging import log_event
import requests
import json

def test_hello(client):
    response = client.get("/")
    assert b'Login' in response.data

#@patch('os.path.exists')
#def test_compare_images_no_name(mocked_exists, client):
#    mocked_exists.return_value = True
#    data = {
#        'file1': (BytesIO(b'test image data 1'), )
#    }
#
#    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)
#
#    assert response.status_code == 200
#    assert b'There was an attempt to compere images' in response.data

@patch('os.path.exists')
def test_compare_images_wrong_extension(mocked_exists, client):
    mocked_exists.return_value = True
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.txt'),
        'file2': (BytesIO(b'test image data 2'), 'file2.txt')
    }

    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert b'Unsupported filetype' in response.data

@patch('app.views.send_compare_request')
def test_compare_images_same_person(mocked_compare, client):
    mocked_compare.return_value = {'is_similar': True, 'similarity_score': 0.9}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 2
    assert b'Similarity_score: 0.9. This is the same person' in response.data

@patch('app.views.send_compare_request')
def test_compare_images_not_same_person(mocked_compare, client):
    mocked_compare.return_value = {'is_similar': False, 'similarity_score': 0.3}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 2
    assert b'Similarity_score: 0.3. This is not the same person' in response.data

@patch('app.views.send_compare_request')
def test_compare_images_error(mocked_compare, client):
    mocked_compare.return_value = {'error': 'some error',
                                   'details': 'error detail',
                                   'status_code': 404,
                                   'correlation_id': 'correlation_id'}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 2
    assert b"Error occurred! Status Code: 404, Error: some error" in response.data

@patch('app.views.send_compare_request')
def test_compare_images_correlation(mocked_compare, client):
    mocked_compare.return_value = {'correlation_id': 'correlation_id'}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_images', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 2
    assert b"Unexpected response from the comparison service" in response.data

def test_allowed_file():
    result1 = allowed_file('file.txt')
    result2 = allowed_file('file.png')
    assert result1 == False
    assert result2 == True

@patch('requests.post')
def test_send_compare_request(mock_post):
    mocked_response = MagicMock()
    mocked_data = 'saf'
    mocked_response.content = "asdf"

#@patch('requests.post')
#@patch('app.logging.log_event')
#def test_send_compare_request_success(mocked_log, mocked_post):
#    mock_response_data = {
#        "is_similar": True,
#        "similarity_score": 0.95
#    }
#    mock_response = requests.Response()
#    mock_response.status_code = 200
#    mock_response.json_data= json.dumps(mock_response_data).encode('utf-8')
#
#    mocked_post.return_value = mock_response
#    result = send_compare_request('test_data/cr77.webp', 'test_data/cr.png')
#    assert result == mock_response_data
#    assert mocked_post.call_count == 1
#    assert mocked_log.call_count == 1

def test_admin_view_perm(admin_login, client):
    response = client.get('/admin', follow_redirects = True)
    assert b'Set Threshold' in response.data
