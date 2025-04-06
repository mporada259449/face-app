import asyncio
import tempfile
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import cv2
import numpy as np
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4

from src_models.models import FACE_VERIFIER
from src_models.models.utils import cosine_similarity
from src_models.request_utils import process_image, process_image_sync


# Initialize a global threshold
CURRENT_THRESHOLD: float = 0.7  # Default threshold
VIDEO_FRAME_SAMPLE_COUNT: int = 5


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifespan: load model on startup, cleanup on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    global FACE_VERIFIER
    print("Loading model during startup...")
    if FACE_VERIFIER is None:
        raise Exception("Model is not initialized!")
    yield
    print("Cleaning up resources during shutdown...")


# Create the FastAPI app with the lifespan hook
app = FastAPI(lifespan=lifespan)


# Threshold management
class Threshold(BaseModel):
    threshold: float


@app.post("/set_threshold")
async def set_threshold(new_threshold: Threshold) -> dict[str, str]:
    """
    Set a new similarity threshold dynamically.

    Args:
        new_threshold (Threshold): The new threshold value.

    Returns:
        dict: A message confirming the update.
    """
    global CURRENT_THRESHOLD
    if not (0 <= new_threshold.threshold <= 1):
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between 0 and 1.",
        )
    CURRENT_THRESHOLD = new_threshold.threshold
    return {"message": f"Threshold updated to {CURRENT_THRESHOLD}"}


@app.post("/faceapp/compare/")
async def compare_faces(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    correlation_id: str = Header(f"{uuid4()}"),
) -> JSONResponse:
    """
    Compare two uploaded face images and return their similarity score.

    Args:
        image1 (UploadFile): The first image to compare.
        image2 (UploadFile): The second image to compare.
        correlation_id (str): A unique identifier for request tracking.

    Returns:
        JSONResponse: The similarity score and whether the faces are similar.
    """
    try:
        # Process both images concurrently
        preprocessed_images = await asyncio.gather(
            process_image(image1), process_image(image2)
        )

        # Compute embeddings and similarity score
        embedding1, embedding2 = FACE_VERIFIER.forward(*preprocessed_images)
        similarity_score: float = float(cosine_similarity(embedding1, embedding2))
        similarity_score: float = (similarity_score + 1) / 2
        is_similar: bool = similarity_score >= CURRENT_THRESHOLD

        return JSONResponse(
            status_code=200,
            content={
                "status_code": 200,
                "similarity_score": similarity_score,
                "is_similar": is_similar,
                "correlation_id": correlation_id,
            },
        )
    except HTTPException as he:
        # Handle HTTP exceptions
        return JSONResponse(
            status_code=he.status_code,
            content={
                "status_code": he.status_code,
                "error": he.detail,
                "correlation_id": correlation_id,
            },
        )
    except Exception as e:
        # Handle all other exceptions
        return JSONResponse(
            status_code=500,
            content={
                "status_code": 500,
                "error": "Internal Server Error",
                "details": str(e),
                "correlation_id": correlation_id,
            },
        )

@app.post("/faceapp/compare_video/")
async def compare_video_faces(
    image: UploadFile = File(...),
    video: UploadFile = File(...),
    correlation_id: str = Header(f"{uuid4()}"),
) -> JSONResponse:
    try:
        # Process the input image asynchronously using process_image.
        image_processed = await process_image(image)

        # Write the entire video to a temporary file.
        video_bytes = await video.read()
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            tmp.flush()

            cap = cv2.VideoCapture(tmp.name)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                raise HTTPException(status_code=400, detail="Invalid video or no frames found.")

            # Get n evenly spaced frame indices.
            frame_indices = np.linspace(0, total_frames - 1, VIDEO_FRAME_SAMPLE_COUNT, dtype=int).tolist()

            # Read each frame at the specified indices.
            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)

        if not frames:
            raise HTTPException(status_code=400, detail="No valid frames extracted from video.")

        # Asynchronously process each frame using process_image_sync.
        async def process_frame(frame: np.ndarray) -> np.ndarray:
            return await asyncio.to_thread(process_image_sync, frame)

        processed_frames = await asyncio.gather(*(process_frame(frame) for frame in frames))

        # For each processed frame, asynchronously call the model to compute similarity with the input image.
        async def process_pair(frame_processed: np.ndarray) -> float:
            embedding_image, embedding_frame = await asyncio.to_thread(FACE_VERIFIER.forward, image_processed, frame_processed)
            score = float(cosine_similarity(embedding_image, embedding_frame))
            return (score + 1) / 2  

        similarity_scores = await asyncio.gather(*(process_pair(frame) for frame in processed_frames))
        aggregated_similarity = sum(similarity_scores) / len(similarity_scores)
        is_similar = aggregated_similarity >= CURRENT_THRESHOLD

        return JSONResponse(
            status_code=200,
            content={
                "status_code": 200,
                "aggregated_similarity": aggregated_similarity,
                "is_similar": is_similar,
                "correlation_id": correlation_id,
            },
        )
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={
                "status_code": he.status_code,
                "error": he.detail,
                "correlation_id": correlation_id,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status_code": 500,
                "error": "Internal Server Error",
                "details": str(e),
                "correlation_id": correlation_id,
            },
        )
