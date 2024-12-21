from enum import Enum
from pathlib import Path

CHECKPOINTS_ROOT = Path.cwd() / "models" / "checkpoints"

class ModelPaths(Enum):
    FACE_DETECTOR = CHECKPOINTS_ROOT / "blaze_face_short_range.tflite"
    FACE_LANDMARKER = CHECKPOINTS_ROOT / "face_landmarker.task"
    ARCFACE = CHECKPOINTS_ROOT / "w600k_r50.onnx"