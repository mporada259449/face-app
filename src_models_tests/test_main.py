import numpy as np
import pytest
import cv2
import io
import asyncio
import contextlib
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src_models.main import app, lifespan
import src_models.main as main_mod

client = TestClient(app)


# Dummy FaceVerifier to simulate predictable embeddings.
class DummyFaceVerifier:
    def forward(self, image1, image2):
        return np.array([1, 0, 0]), np.array([1, 0, 0])


@pytest.fixture(autouse=True)
def patch_face_verifier(monkeypatch):
    """Patch FACE_VERIFIER and image processing functions to avoid external dependencies."""
    monkeypatch.setattr(main_mod, "FACE_VERIFIER", DummyFaceVerifier())

    async def fake_process_image(file):
        return np.ones((1, 3, 112, 112), dtype=np.float32)

    monkeypatch.setattr(main_mod, "process_image", fake_process_image)

    monkeypatch.setattr(
        main_mod,
        "process_image_sync",
        lambda frame: np.ones((1, 3, 112, 112), dtype=np.float32),
    )


# Threshold endpoints tests
def test_set_threshold_valid():
    """Test setting a valid threshold."""
    response = client.post("/set_threshold", json={"threshold": 0.8})
    assert response.status_code == 200
    assert "Threshold updated to 0.8" in response.json()["message"]


def test_set_threshold_invalid():
    """Test that setting an invalid threshold returns an error."""
    response = client.post("/set_threshold", json={"threshold": 1.5})
    assert response.status_code == 400


# compare_faces endpoint tests
def test_compare_faces():
    """Test compare_faces endpoint returns correct similarity score."""
    files = {
        "image1": ("test.jpg", b"fake image data", "image/jpeg"),
        "image2": ("test.jpg", b"fake image data", "image/jpeg"),
    }
    response = client.post("/faceapp/compare/", files=files)
    json_data = response.json()
    assert response.status_code == 200
    assert "similarity_score" in json_data
    assert json_data["similarity_score"] == 1.0


def test_compare_faces_internal_error(monkeypatch):
    """Test compare_faces endpoint handling of internal errors."""

    def fake_process_image(file):
        raise Exception("Test compare_faces error")

    monkeypatch.setattr(main_mod, "process_image", fake_process_image)
    files = {
        "image1": ("test.jpg", b"fake image data", "image/jpeg"),
        "image2": ("test.jpg", b"fake image data", "image/jpeg"),
    }
    response = client.post("/faceapp/compare/", files=files)
    json_data = response.json()
    assert response.status_code == 500
    assert "Internal Server Error" in json_data["error"]
    assert "Test compare_faces error" in json_data["details"]


# compare_video endpoint tests
def test_compare_video_no_frames(monkeypatch):
    """Test compare_video endpoint returns error when video has zero frames."""

    class DummyCapZero:
        def __init__(self, filename):
            self.frames = []

        def get(self, prop):
            return 0 if prop == cv2.CAP_PROP_FRAME_COUNT else 0

        def set(self, prop, value):
            pass

        def read(self):
            return False, None

    monkeypatch.setattr("src_models.main.cv2.VideoCapture", lambda x: DummyCapZero(x))
    files = {
        "image": ("test.jpg", b"fake image data", "image/jpeg"),
        "video": ("test.mp4", b"fake video data", "video/mp4"),
    }
    response = client.post("/faceapp/compare_video/", files=files)
    json_data = response.json()
    assert response.status_code == 400
    assert "Invalid video or no frames found" in json_data["error"]


def test_compare_video_no_valid_frames(monkeypatch):
    """Test compare_video endpoint returns error when no valid frames are extracted."""

    class DummyCapNoValid:
        def __init__(self, filename):
            self.frames = [None] * 10

        def get(self, prop):
            return 10 if prop == cv2.CAP_PROP_FRAME_COUNT else 0

        def set(self, prop, value):
            pass

        def read(self):
            return False, None

    monkeypatch.setattr(
        "src_models.main.cv2.VideoCapture", lambda x: DummyCapNoValid(x)
    )
    files = {
        "image": ("test.jpg", b"fake image data", "image/jpeg"),
        "video": ("test.mp4", b"fake video data", "video/mp4"),
    }
    response = client.post("/faceapp/compare_video/", files=files)
    json_data = response.json()
    assert response.status_code == 400
    assert "No valid frames extracted from video" in json_data["error"]


def test_compare_video_internal_error(monkeypatch):
    """Test compare_video endpoint handling of internal errors during frame processing."""
    monkeypatch.setattr(
        main_mod,
        "process_image_sync",
        lambda frame: (_ for _ in ()).throw(Exception("Video frame error")),
    )

    class DummyCapValid:
        def __init__(self, filename):
            self.frames = [np.ones((100, 100, 3), dtype=np.uint8)] * 10

        def get(self, prop):
            return len(self.frames) if prop == cv2.CAP_PROP_FRAME_COUNT else 0

        def set(self, prop, value):
            pass

        def read(self):
            return True, self.frames[0]

    monkeypatch.setattr("src_models.main.cv2.VideoCapture", lambda x: DummyCapValid(x))
    files = {
        "image": ("test.jpg", b"fake image data", "image/jpeg"),
        "video": ("test.mp4", b"fake video data", "video/mp4"),
    }
    response = client.post("/faceapp/compare_video/", files=files)
    json_data = response.json()
    assert response.status_code == 500
    assert "Internal Server Error" in json_data["error"]
    assert "Video frame error" in json_data["details"]


def test_compare_faces_http_exception(monkeypatch):
    """Test compare_faces endpoint HTTP exception branch."""

    def fake_process_image(file):
        raise HTTPException(status_code=400, detail="Forced HTTP error")

    monkeypatch.setattr(main_mod, "process_image", fake_process_image)
    files = {
        "image1": ("test.jpg", b"fake image data", "image/jpeg"),
        "image2": ("test.jpg", b"fake image data", "image/jpeg"),
    }
    response = client.post("/faceapp/compare/", files=files)
    json_data = response.json()
    assert response.status_code == 400
    assert "Forced HTTP error" in json_data["error"]


def test_lifespan_startup_error(monkeypatch):
    """Test that the lifespan context manager raises an exception if FACE_VERIFIER is None."""
    monkeypatch.setattr(main_mod, "FACE_VERIFIER", None)

    async def run_lifespan():
        async with lifespan(app):
            pass

    with pytest.raises(Exception, match="Model is not initialized!"):
        asyncio.run(run_lifespan())


def test_lifespan_shutdown_print():
    """Test that the lifespan context manager prints shutdown message."""
    f = io.StringIO()

    async def run_lifespan():
        async with lifespan(app):
            pass

    with contextlib.redirect_stdout(f):
        asyncio.run(run_lifespan())
    output = f.getvalue()
    assert "Cleaning up resources during shutdown..." in output
