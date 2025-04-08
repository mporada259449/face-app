import numpy as np
import pytest
import cv2
from fastapi import HTTPException
from src_models.models.face_detector import FaceDetector
from src_models.models.utils import detect_align_crop_face, align_face


# Dummy classes to simulate MediaPipe detection results
class DummyBoundingBox:
    def __init__(self, bbox):
        self.origin_x, self.origin_y, self.width, self.height = bbox


class DummyDetection:
    def __init__(self, bbox):
        self.bounding_box = DummyBoundingBox(bbox)


class DummyDetector:
    def __init__(self, detections):
        self._detections = detections

    def detect(self, mp_image):
        # Return a dummy result with provided detections.
        class DummyResult:
            def __init__(self, detections):
                self.detections = detections

        return DummyResult(self._detections)


@pytest.fixture
def face_detector():
    """Fixture returning a FaceDetector instance with a dummy detector."""
    detector = FaceDetector()
    dummy_bbox = (10, 20, 100, 200)
    dummy_detection = DummyDetection(dummy_bbox)
    detector.face_detector = DummyDetector([dummy_detection])
    return detector


def test_detect_face_returns_bbox(face_detector):
    """Test that detect_face returns the expected bounding box."""
    dummy_image = np.zeros((300, 300, 3), dtype=np.uint8)
    bbox = face_detector.detect_face(dummy_image)
    assert bbox == (10, 20, 100, 200)


def test_detect_face_no_detection(face_detector):
    """Test that detect_face returns None when no face is detected."""
    face_detector.face_detector = DummyDetector([])
    dummy_image = np.zeros((300, 300, 3), dtype=np.uint8)
    assert face_detector.detect_face(dummy_image) is None


def test_crop_face(face_detector):
    """Test the crop_face method using computed margins and vertical shift."""
    dummy_image = np.arange(400 * 400 * 3).reshape((400, 400, 3)).astype(np.uint8)
    face_coords = (50, 50, 100, 100)
    cropped = face_detector.crop_face(dummy_image, face_coords)
    margin = int(100 * face_detector.margin)
    vertical_shift = int(100 * face_detector.vertical_shift_percentage)
    new_y = max(50 - vertical_shift, 0)
    x_start = max(50 - margin, 0)
    y_start = max(new_y - margin, 0)
    x_end = min(50 + 100 + margin, 400)
    y_end = min(new_y + 100 + margin, 400)
    expected = dummy_image[y_start:y_end, x_start:x_end]
    np.testing.assert_array_equal(cropped, expected)


def test_detect_align_crop_face_no_face(monkeypatch):
    """Test that detect_align_crop_face raises an HTTPException when no face is detected."""
    dummy_image = np.ones((500, 500, 3), dtype=np.uint8) * 255

    # Landmark detector returns valid dummy landmarks.
    class DummyLandmarker:
        def detect_landmarks(self, image):
            landmarks = np.zeros((500, 2), dtype=np.float32)
            landmarks[468] = [0.5, 0.5]
            landmarks[473] = [0.6, 0.5]
            landmarks[4] = [0.55, 0.55]
            landmarks[291] = [0.45, 0.7]
            landmarks[61] = [0.65, 0.7]
            return landmarks

    monkeypatch.setattr("src_models.models.utils.FACE_LANDMARKER", DummyLandmarker())

    # Simulate no detected face by face detector
    class DummyDetectorNoFace:
        def detect_face(self, image):
            return None

        def crop_face(self, image, face_coords):
            return image

    monkeypatch.setattr("src_models.models.utils.FACE_DETECTOR", DummyDetectorNoFace())

    with pytest.raises(HTTPException) as excinfo:
        detect_align_crop_face(dummy_image)
    assert "No face detected!" in str(excinfo.value)


def test_align_face_failure(monkeypatch):
    """Test that align_face raises ValueError when cv2.estimateAffinePartial2D fails."""
    dummy_image = np.ones((500, 500, 3), dtype=np.uint8) * 255
    dummy_landmarks = np.zeros((500, 2), dtype=np.float32)
    dummy_landmarks[468] = [0.5, 0.5]
    dummy_landmarks[473] = [0.6, 0.5]
    dummy_landmarks[4] = [0.55, 0.55]
    dummy_landmarks[291] = [0.45, 0.7]
    dummy_landmarks[61] = [0.65, 0.7]
    monkeypatch.setattr(
        cv2, "estimateAffinePartial2D", lambda src, dst, method: (None, None)
    )
    with pytest.raises(ValueError) as excinfo:
        align_face(dummy_image, dummy_landmarks)
    assert "Failed to compute affine transformation matrix" in str(excinfo.value)
