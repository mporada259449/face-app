import os
import io
import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    app.config['SECRET_KEY'] = 'test_secret_key'  # Ensure the secret key is set
    app.config['UPLOAD_FOLDER'] = '/mnt/images'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

def test_home_route(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    print(response.data.decode())  # Print the response data to debug
    assert b'Face-app' in response.data  # Adjust the text to match the actual content

def test_compare_images_route(client):
    """Test the compare images route."""
    # Ensure the upload folder exists
    upload_folder = '/mnt/images'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    data = {
        'image1': (io.BytesIO(b'my file contents'), 'test1.jpg'),
        'image2': (io.BytesIO(b'my file contents'), 'test2.jpg')
    }
    response = client.post('/compare_images', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'Images compared successfully' in response.data