import asyncio
import cv2
import pytest
import numpy as np
from fastapi import HTTPException
from src_models.request_utils import (
    validate_file_extension,
    validate_file_mime,
    process_image,
    process_image_sync,
)


def test_validate_file_extension_valid():
    """Test valid file extensions do not raise an error."""
    validate_file_extension("test.jpg")
    validate_file_extension("image.PNG")


def test_validate_file_extension_invalid():
    """Test that an invalid file extension raises HTTPException."""
    with pytest.raises(HTTPException):
        validate_file_extension("document.txt")


def test_validate_file_mime(monkeypatch):
    """Test that a supported MIME type passes validation."""

    class DummyMagic:
        def __init__(self, **kwargs):
            pass

        def from_buffer(self, data):
            return "image/jpeg"

    monkeypatch.setattr(
        "src_models.request_utils.magic.Magic", lambda **kwargs: DummyMagic()
    )
    validate_file_mime(b"dummy data")


def test_process_image_sync(monkeypatch):
    """Test process_image_sync returns preprocessed image with correct shape."""
    dummy_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    monkeypatch.setattr(
        "src_models.request_utils.detect_align_crop_face",
        lambda img: (img, np.array([[0, 0]])),
    )
    monkeypatch.setattr(
        "src_models.request_utils.preprocess_image_direct",
        lambda img: np.ones((1, 3, 112, 112), dtype=np.float32),
    )
    result = process_image_sync(dummy_image)
    assert result.shape == (1, 3, 112, 112)


def test_validate_file_mime_invalid(monkeypatch):
    """Test that an unsupported MIME type raises HTTPException."""

    class DummyMagic:
        def __init__(self, **kwargs):
            pass

        def from_buffer(self, data):
            return "application/pdf"

    monkeypatch.setattr(
        "src_models.request_utils.magic.Magic", lambda **kwargs: DummyMagic()
    )
    with pytest.raises(HTTPException) as excinfo:
        validate_file_mime(b"dummy data")
    assert "Unsupported MIME type" in str(excinfo.value)


def test_process_image_invalid_image(monkeypatch):
    """Test that process_image raises an error when image decoding fails."""

    monkeypatch.setattr(cv2, "imdecode", lambda arr, flag: None)

    class DummyMagicValid:
        def __init__(self, **kwargs):
            pass

        def from_buffer(self, data):
            return "image/jpeg"

    monkeypatch.setattr(
        "src_models.request_utils.magic.Magic", lambda **kwargs: DummyMagicValid()
    )

    class DummyUploadFile:
        def __init__(self, filename, content):
            self.filename = filename
            self._content = content

        async def read(self):
            return self._content

    dummy_file = DummyUploadFile("test.jpg", b"dummy image data")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(process_image(dummy_file))
    assert "Invalid or corrupted image file" in str(excinfo.value)
