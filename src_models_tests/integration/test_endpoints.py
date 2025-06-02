import os
import pytest
from fastapi.testclient import TestClient
from src_models.main import app

# Directory for test assets
TEST_IMAGES_DIR = "test_images"


@pytest.fixture
def clear_face_path():
    """Return the path for a clear face image."""
    return os.path.join(TEST_IMAGES_DIR, "clear_face.png")


@pytest.fixture
def mountains_path():
    """Return the path for a mountains image."""
    return os.path.join(TEST_IMAGES_DIR, "mountain.webp")


@pytest.fixture
def test_video_path():
    """Return the path for a test video."""
    return os.path.join(TEST_IMAGES_DIR, "test_video.mp4")


client = TestClient(app)


def test_compare_faces_success(clear_face_path):
    """Integration test: compare_faces should return high similarity for identical images."""
    with open(clear_face_path, "rb") as img1, open(clear_face_path, "rb") as img2:
        files = {
            "image1": ("clear_face.jpg", img1.read(), "image/jpeg"),
            "image2": ("clear_face.jpg", img2.read(), "image/jpeg"),
        }
    response = client.post("/faceapp/compare/", files=files)
    data = response.json()
    assert response.status_code == 200, response.json()
    assert "similarity_score" in data
    assert data["similarity_score"] >= 0.7


def test_compare_faces_failure(clear_face_path, mountains_path):
    """Integration test: compare_faces should fail when using an image without a face."""
    with open(clear_face_path, "rb") as clear_img, open(
        mountains_path, "rb"
    ) as mountain_img:
        files = {
            "image1": ("clear_face.jpg", clear_img.read(), "image/jpeg"),
            "image2": ("mountains.jpg", mountain_img.read(), "image/jpeg"),
        }
    response = client.post("/faceapp/compare/", files=files)
    data = response.json()
    assert response.status_code == 400, response.json()
    assert "error" in data


def test_compare_video_faces_success(clear_face_path, test_video_path):
    """Integration test: compare_video should return an aggregated similarity score within [0, 1]."""
    with open(clear_face_path, "rb") as clear_img, open(
        test_video_path, "rb"
    ) as video_file:
        files = {
            "image": ("clear_face.jpg", clear_img.read(), "image/jpeg"),
            "video": ("test.mp4", video_file.read(), "video/mp4"),
        }
    response = client.post("/faceapp/compare_video/", files=files)
    data = response.json()
    assert response.status_code == 200, response.json()
    assert "similarity_score" in data
    assert 0 <= data["similarity_score"] <= 1
