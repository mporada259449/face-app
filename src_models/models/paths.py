from enum import Enum
from pathlib import Path

CHECKPOINTS_ROOT = Path.cwd() / "src_models" / "models" / "checkpoints"

class ModelPaths(Enum):
    FACE_DETECTOR = CHECKPOINTS_ROOT / "blaze_face_short_range.tflite"
    FACE_LANDMARKER = CHECKPOINTS_ROOT / "face_landmarker.task"
    FACE_EMBEDDER = CHECKPOINTS_ROOT / "face_embedder.onnx"