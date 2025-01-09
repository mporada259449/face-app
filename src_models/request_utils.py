import cv2
import magic
import numpy as np
from fastapi import HTTPException, UploadFile

from models.utils import detect_align_crop_face
from models.face_verifier import preprocess_image_direct

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".tiff", ".webp")
ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "image/tiff", "image/webp")


def validate_file_extension(filename: str) -> None:
    """
    Validate the file extension.

    Args:
        filename (str): The name of the uploaded file.

    Raises:
        HTTPException: If the file extension is not allowed.
    """
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail=f"Unsupported file extension: {filename}"
        )


def validate_file_mime(image_data: bytes) -> None:
    """
    Validate the MIME type of a file using its content.

    Args:
        image_data (bytes): The binary content of the uploaded image.

    Raises:
        HTTPException: If the MIME type is not allowed.
    """
    mime_type = magic.Magic(mime=True).from_buffer(image_data)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, detail=f"Unsupported MIME type: {mime_type}"
        )


def process_image_sync(image: np.ndarray) -> np.ndarray:
    """
    Detect, align, and preprocess a face image.

    Args:
        image (np.ndarray): The input image as a NumPy array.

    Returns:
        np.ndarray: The preprocessed image.

    Raises:
        ValueError: If face detection or preprocessing fails.
    """
    try:
        aligned_image, _ = detect_align_crop_face(image)
        preprocessed_image = preprocess_image_direct(aligned_image)
        return preprocessed_image
    except Exception as e:
        raise ValueError(f"Error during image preprocessing: {str(e)}")


async def process_image(file: UploadFile) -> np.ndarray:
    """
    Validate and preprocess an uploaded image file.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        np.ndarray: The preprocessed image ready for model inference.

    Raises:
        HTTPException: If validation or processing fails.
    """
    # Validate file extension
    validate_file_extension(file.filename)

    # Read image binary data
    image_data = await file.read()

    # Validate MIME type
    validate_file_mime(image_data)

    # Decode image using OpenCV
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

    # Perform synchronous image processing
    preprocessed_image = process_image_sync(image)

    return preprocessed_image
