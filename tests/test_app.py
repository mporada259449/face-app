import pytest
from unittest.mock import patch
from flask import Flask, request
import io

@pytest.fixture
def client():
    app = Flask(__name__)

    @app.route('/compare_images', methods=['POST'])
    def compare_images():
        if 'file' not in request.files:
            return 'No file was provided', 400
        # Add more logic here as needed
        return 'File received', 200

    app.testing = True
    return app.test_client()

def test_compare_images_no_files(client):
    """Test the /compare_images route when no files are provided."""
    with client.application.test_request_context('/compare_images', method='POST'):
        with patch('flask.request.files', create=True) as mocked_files:
            mocked_files.__contains__.return_value = False
            
            response = client.post('/compare_images')
            assert response.status_code == 400
            assert b'No file was provided' in response.data

def test_compare_images_with_file(client):
    """Test the /compare_images route when a file is provided."""
    data = {
        'file': (io.BytesIO(b'my file contents'), 'test.jpg')
    }
    response = client.post('/compare_images', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'File received' in response.data