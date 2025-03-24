import pytest
import cv2
import numpy as np
from pathlib import Path
from fastapi import HTTPException
from models.utils import detect_align_crop_face, align_face, cosine_similarity
from models.face_verifier import preprocess_image_direct

# Define the test data directory
TEST_DATA_DIR = Path("test_images/")


@pytest.fixture
def load_image():
    """Helper function to load test images."""
    def _load_image(filename: str):
        path = TEST_DATA_DIR / filename
        if not path.exists():
            pytest.fail(f"Test file does not exist: {path}")
        image = cv2.imread(str(path))
        if image is None:
            pytest.fail(f"Failed to load image: {path}")
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
    return _load_image


def test_detect_align_crop_face_with_face(load_image):
    """Test the detect_align_crop_face function with an image containing a face."""
    image = load_image("cr.png")
    aligned_face, landmarks = detect_align_crop_face(image)
    
    assert aligned_face is not None
    assert aligned_face.shape == (112, 112, 3)  # Example expected shape
    assert landmarks is not None
    assert landmarks.shape[1] == 2  # Landmarks should have (x, y) coordinates


def test_detect_align_crop_face_no_face(load_image):
    """Test the detect_align_crop_face function with an image without a face."""
    image = load_image("wheat.jpg")
    with pytest.raises(HTTPException) as excinfo:
        detect_align_crop_face(image)
    assert excinfo.value.detail == "No valid landmarks detected!"


def test_detect_align_crop_face_invalid_image():
    """Test the detect_align_crop_face function with a corrupted or invalid image."""
    corrupted_image_path = TEST_DATA_DIR / "requirements.in"
    if not corrupted_image_path.exists():
        pytest.fail(f"Test file does not exist: {corrupted_image_path}")
    image = cv2.imread(str(corrupted_image_path))
    if image is None:
        pytest.fail(f"Failed to load corrupted image: {corrupted_image_path}")

    with pytest.raises(HTTPException) as excinfo:
        detect_align_crop_face(image)
    assert excinfo.value.detail == "Invalid or corrupted image file"


def test_align_face_with_valid_landmarks(load_image):
    """Test the align_face function with valid input."""
    image = load_image("cr.png")
    landmarks = np.array([
        [100, 200],  # Right eye
        [150, 200],  # Left eye
        [125, 250],  # Nose tip
        [100, 300],  # Right mouth corner
        [150, 300],  # Left mouth corner
    ], dtype=np.float32)

    aligned_image, transformed_landmarks = align_face(image, landmarks)

    assert aligned_image is not None
    assert aligned_image.shape == (616, 616, 3)  # Example shape for the aligned output
    assert transformed_landmarks.shape == landmarks.shape


def test_preprocess_image_direct(load_image):
    """Test preprocessing of an aligned face image."""
    image = load_image("cr.png")
    preprocessed = preprocess_image_direct(image)

    assert preprocessed is not None
    assert preprocessed.shape == (1, 3, 112, 112)  # Batch, Channels, Height, Width
    assert preprocessed.dtype == np.float32
    assert np.all(preprocessed >= -1) and np.all(preprocessed <= 1)  # Normalized


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    embedding1 = np.array([1, 0, 0], dtype=np.float32)
    embedding2 = np.array([0, 1, 0], dtype=np.float32)
    embedding3 = np.array([1, 1, 0], dtype=np.float32)

    assert cosine_similarity(embedding1, embedding2) == pytest.approx(0.0, 0.01)
    assert cosine_similarity(embedding1, embedding3) == pytest.approx(0.7071, 0.01)
    assert cosine_similarity(embedding3, embedding3) == pytest.approx(1.0, 0.01)