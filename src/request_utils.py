import mimetypes
import cv2
from fastapi import HTTPException
from models.utils import detect_align_crop_face
from models.face_verifier import preprocess_image_direct
import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import UploadFile, HTTPException

import os
from pathlib import Path

import tempfile
executor = ProcessPoolExecutor()  # For parallel CPU-bound tasks

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/tiff", "image/webp"}

def validate_file_extension(filename: str):
    """
    Validate the file extension.
    """
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {filename}")


def validate_file_mime(temp_file):
    # """
    # Validate the MIME type of a file.
    # """
    # print(temp_file.name)
    # mime_type, _ = mimetypes.guess_type(temp_file.name)
    # if mime_type not in ALLOWED_MIME_TYPES:
    #     raise HTTPException(status_code=400, detail=f"Unsupported MIME type: {mime_type}")
    pass

# import magic

# def validate_file_mime(temp_file):
#     """
#     Validate the MIME type of a file using its content.
#     """
#     temp_file.seek(0)  # Ensure the file pointer is at the start
#     mime_type = magic.Magic(mime=True).from_file(temp_file.name)

#     if mime_type not in ALLOWED_MIME_TYPES:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Unsupported MIME type: {mime_type}. Allowed types are {', '.join(ALLOWED_MIME_TYPES)}."
#         )
    
def process_image_sync(image_path):
    """
    Detect, align, and preprocess a face image. This function runs in a separate process.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Invalid image file")

        aligned_image, _ = detect_align_crop_face(image)
        preprocessed_image = preprocess_image_direct(aligned_image)
        return preprocessed_image
    except Exception as e:
        raise ValueError(f"Error during image preprocessing: {str(e)}")
    
async def process_image(file: UploadFile):
    """
    Validate and preprocess an uploaded image file incrementally.
    """
    # Validate file extension
    validate_file_extension(file.filename)

    # Create a temporary file path using tempfile.mkstemp
    temp_file_descriptor, temp_file_path = tempfile.mkstemp(suffix=Path(file.filename).suffix)
    os.close(temp_file_descriptor)  # Close the file descriptor immediately to unlock the file

    try:
        # Open the file for writing and incrementally save the uploaded file content
        with open(temp_file_path, "wb") as temp_file:
            first_chunk = await file.read(1024)  # Read the first chunk for validation
            temp_file.write(first_chunk)

            # Validate MIME type of the first chunk
            validate_file_mime(temp_file)

            # Continue writing the remaining chunks
            while chunk := await file.read(1024):
                temp_file.write(chunk)

        # Run the heavy preprocessing task in a separate process
        loop = asyncio.get_event_loop()
        preprocessed_image = await loop.run_in_executor(executor, process_image_sync, temp_file_path)
        return preprocessed_image
    finally:
        # Ensure the temporary file is deleted after processing
        os.remove(temp_file_path)
