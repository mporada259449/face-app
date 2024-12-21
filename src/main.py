# Initialize the FastAPI app
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from uuid import uuid4
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from models import FACE_VERIFIER

from models.utils import cosine_similarity
from request_utils import process_image


# Initialize a global threshold and executor
current_threshold = 0.5  # Default threshold

@asynccontextmanager
async def lifespan(app: FastAPI):
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
async def set_threshold(new_threshold: Threshold):
    """
    Set a new similarity threshold dynamically.
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
):
    """
    Compare two uploaded face images and return their similarity score.
    """
    try:
        # Process both images concurrently
        preprocessed_images = await asyncio.gather(
            process_image(image1),
            process_image(image2)
        )
        # Compute embeddings and similarity score
        embedding1, embedding2 = FACE_VERIFIER.forward(*preprocessed_images)
        similarity_score = cosine_similarity(embedding1, embedding2)

        # Compare with the current threshold
        is_similar = similarity_score >= current_threshold

        return JSONResponse(content={"similarity_score": float(similarity_score), "is_similar": bool(is_similar)})
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")