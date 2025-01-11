from .face_detector import FaceDetector
from .face_landmarker import FaceLandmarker
from .face_verifier import ArcFaceBackbone
from .face_verifier import SiameseNetwork


FACE_DETECTOR = FaceDetector()
FACE_LANDMARKER = FaceLandmarker()
ARCFACE_MODEL = ArcFaceBackbone()
FACE_VERIFIER = SiameseNetwork(ARCFACE_MODEL)