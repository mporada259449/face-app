from unittest.mock import patch, MagicMock
from io import BytesIO
from app.views import allowed_file, send_compare_request
from app.logging import log_event
import requests
import json

def test_hello(client):
    response = client.get("/")
    assert b'Login' in response.data

@patch('os.path.exists')
def test_compare_images_wrong_extension(mocked_exists, client):
    mocked_exists.return_value = True
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.txt'),
        'file2': (BytesIO(b'test image data 2'), 'file2.txt')
    }

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert b'Unsupported filetype' in response.data

@patch('app.views.send_compare_request')
def test_compare_images_same_person(mocked_compare, client):
    mocked_compare.return_value = {'is_similar': True, 'similarity_score': 0.9}
    data = {
        'video1': (BytesIO(b'test video data'), ''), 
        'image1': (BytesIO(b'test image data 1'), 'file1.png'),
        'image2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 3
    assert b'Similarity_score: 0.9. This is the same person' in response.data

@patch('app.views.send_compare_request')
def test_compare_video_same_person(mocked_compare, client):
    mocked_compare.return_value = {'is_similar': True, 'similarity_score': 0.9}
    data = {
        'image1': (BytesIO(b'test video data'), ''), 
        'video1': (BytesIO(b'test image data 1'), 'file1.mp4'),
        'image2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 3
    assert b'Similarity_score: 0.9. This is the same person' in response.data

@patch('app.views.send_compare_request')
def test_compare_images_not_same_person(mocked_compare, client):
    mocked_compare.return_value = {'is_similar': False, 'similarity_score': 0.3}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 3
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

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 3
    assert b"Error occurred! Status Code: 404, Error: some error" in response.data

@patch('app.views.send_compare_request')
def test_compare_images_correlation(mocked_compare, client):
    mocked_compare.return_value = {'correlation_id': 'correlation_id'}
    data = {
        'file1': (BytesIO(b'test image data 1'), 'file1.png'),
        'file2': (BytesIO(b'test image data 2'), 'file2.png')
    }

    response = client.post('/compare_media', data=data, content_type='multipart/form-data', follow_redirects = True)

    assert response.status_code == 200
    assert mocked_compare.call_count == 1
    assert len(mocked_compare.call_args[1].keys()) == 3
    assert b"Unexpected response from the comparison service" in response.data

def test_allowed_file():
    result1 = allowed_file('file.txt')
    result2 = allowed_file('file.png')
    assert result1 == False
    assert result2 == True
