from .face_detector import FaceDetector
from .face_landmarker import FaceLandmarker
from .face_verifier import FaceEmbedderBackbone
from .face_verifier import SiameseNetwork


FACE_DETECTOR = FaceDetector()
FACE_LANDMARKER = FaceLandmarker()
FACE_EMBEDDER = FaceEmbedderBackbone()
FACE_VERIFIER = SiameseNetwork(FACE_EMBEDDER)