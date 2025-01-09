import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4

from models import FACE_VERIFIER
from models.utils import cosine_similarity
from request_utils import process_image


# Initialize a global threshold
current_threshold: float = 0.5  # Default threshold


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
    global current_threshold
    if not (0 <= new_threshold.threshold <= 1):
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between 0 and 1.",
        )
    current_threshold = new_threshold.threshold
    return {"message": f"Threshold updated to {current_threshold}"}


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
        is_similar: bool = similarity_score >= current_threshold

        return JSONResponse(
            content={"similarity_score": similarity_score, "is_similar": is_similar}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")