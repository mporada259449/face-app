import numpy as np
import pytest
from src_models.models.face_landmarker import FaceLandmarker, Landmark


class DummyLandmarker:
    def __init__(self, landmarks):
        self._landmarks = landmarks

    def detect(self, mp_image):
        # Return a dummy result with the provided landmarks.
        class DummyResult:
            def __init__(self, landmarks):
                self.face_landmarks = [landmarks]

        return DummyResult(self._landmarks)


@pytest.fixture
def face_landmarker():
    lm = FaceLandmarker()
    dummy_landmarks = [Landmark(0.1, 0.2), Landmark(0.3, 0.4)]
    lm.landmarker = DummyLandmarker(dummy_landmarks)
    return lm


def test_landmark_repr():
    """Test the __repr__ method of Landmark."""
    landmark = Landmark(0.12345, 0.98765)
    expected = "Landmark(x=0.12, y=0.99)"
    assert repr(landmark) == expected


def test_detect_landmarks(face_landmarker):
    """Test detect_landmarks returns denormalized landmark coordinates."""
    dummy_face = np.ones((100, 100, 3), dtype=np.uint8) * 255
    landmarks = face_landmarker.detect_landmarks(dummy_face)
    expected = np.array(
        [[0.1 * 100, 0.2 * 100], [0.3 * 100, 0.4 * 100]], dtype=np.float32
    )
    np.testing.assert_allclose(landmarks, expected, rtol=1e-2)


def test_detect_landmarks_none(face_landmarker):
    """Test detect_landmarks returns None when no landmarks are found."""

    class DummyResult:
        face_landmarks = []

    face_landmarker.landmarker.detect = lambda mp_image: DummyResult()
    dummy_face = np.ones((100, 100, 3), dtype=np.uint8) * 255
    result = face_landmarker.detect_landmarks(dummy_face)
    assert result is None


def test_detect_landmarks_invalid_input(face_landmarker):
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError):
        face_landmarker.detect_landmarks(None)
