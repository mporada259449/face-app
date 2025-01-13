from unittest.mock import patch, MagicMock

def test_hello(client):
    response = client.get("/")
    assert b'Login' in response.data

#@patch('app.views.request.files')
#def test_compare_images_no_files(client):
#    #mocked_files.return_value = False
#    response = client.post('/compare_images')
#    assert b'No file was provided' in response.data

def test_compare_images_no_files(client):
    """Test the /compare_images route when no files are provided."""
    with patch('flask.request.files', create=True) as mocked_files:
        mocked_files.__contains__.return_value = False
        
        response = client.post('/compare_images')
        assert response.status_code == 400
        assert b'No file was provided' in response.data

#def test_compare_images(clinet):
#    pass
