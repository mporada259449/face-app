import numpy as np
import pytest
from src_models.models.utils import align_face, cosine_similarity


# Dummy classes for global patching in utils tests
class DummyLandmarker:
    def detect_landmarks(self, image):
        landmarks = np.zeros((500, 2), dtype=np.float32)
        landmarks[468] = [0.5, 0.5]
        landmarks[473] = [0.6, 0.5]
        landmarks[4] = [0.55, 0.55]
        landmarks[291] = [0.45, 0.7]
        landmarks[61] = [0.65, 0.7]
        return landmarks


class DummyDetector:
    def detect_face(self, image):
        return (50, 50, 100, 100)

    def crop_face(self, image, face_coords):
        x, y, w, h = face_coords
        return image[y : y + h, x : x + w]


import src_models.models.utils as utils


@pytest.fixture(autouse=True)
def patch_global_models(monkeypatch):
    """Patch FACE_LANDMARKER and FACE_DETECTOR in utils with dummy implementations."""
    monkeypatch.setattr(utils, "FACE_LANDMARKER", DummyLandmarker())
    monkeypatch.setattr(utils, "FACE_DETECTOR", DummyDetector())


def test_align_face_success():
    """Test that align_face returns an aligned image and transformed landmarks."""
    dummy_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
    landmarks = np.zeros((500, 2), dtype=np.float32)
    landmarks[468] = [251, 272]
    landmarks[473] = [364, 272]
    landmarks[4] = [308, 336]
    landmarks[291] = [355, 402]
    landmarks[61] = [262, 402]
    aligned_img, transformed_landmarks = align_face(dummy_image, landmarks)
    assert aligned_img.shape == (616, 616, 3)
    assert transformed_landmarks.shape[1] == 2


def test_cosine_similarity():
    """Test that cosine_similarity computes correctly for orthogonal vectors."""
    emb1 = np.array([1, 0])
    emb2 = np.array([0, 1])
    similarity = cosine_similarity(emb1, emb2)
    assert abs(similarity) < 1e-6
