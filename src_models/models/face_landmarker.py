import numpy as np
import mediapipe as mp
from .paths import ModelPaths
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Any, List, Tuple, Optional


class Landmark:
    """
    Represents a facial landmark with x and y coordinates.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Landmark(x={self.x:.2f}, y={self.y:.2f})"


class FaceLandmarker:
    """
    A class to detect facial landmarks using MediaPipe's Face Landmarker API.
    """

    def __init__(
        self,
        model_path: str = ModelPaths.FACE_LANDMARKER.value,
        device: str = "cpu",
        max_faces: int = 1,
    ):
        """
        Initialize the FaceLandmarker with the MediaPipe model and parameters.

        Parameters:
        - model_path (str): Path to the MediaPipe Face Landmarker model file.
        - device (str): Device to run the model on ("cpu" or "cuda").
        - max_faces (int): Maximum number of faces to detect landmarks for.
        """
        self.model_path = model_path
        self.device = device
        self.max_faces = max_faces
        self.landmarker = self._load_model()

    def _load_model(self) -> Any:
        """
        Load the MediaPipe Face Landmarker model.

        Returns:
        - Any: The loaded landmark detection model.
        """
        delegate_device = (
            python.BaseOptions.Delegate.GPU
            if self.device == "cuda"
            else python.BaseOptions.Delegate.CPU
        )
        base_options = python.BaseOptions(
            model_asset_path=self.model_path, delegate=delegate_device
        )
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,  # Set to True if blendshapes are needed
            output_facial_transformation_matrixes=False,  # Set to True if transformation matrices are needed
            num_faces=self.max_faces,
        )
        return vision.FaceLandmarker.create_from_options(options)

    def detect_landmarks(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect facial landmarks in a given cropped face image.

        Parameters:
        - face_image (np.ndarray): Cropped face image (RGB format) as a NumPy array.

        Returns:
        - Optional[np.ndarray]: A NumPy array of shape (n, 2) containing (x, y) coordinates
                                for each detected landmark, or None if no landmarks are found.
        """
        if face_image is None:
            raise ValueError("Input face image cannot be None.")

        # Convert the image to MediaPipe format
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, data=face_image.astype(np.uint8)
        )

        # Detect landmarks
        result = self.landmarker.detect(mp_image)
        if not result.face_landmarks:
            return None  # No landmarks detected

        # Extract landmarks as a NumPy array
        landmarks = np.array(
            [(landmark.x, landmark.y) for landmark in result.face_landmarks[0]],
            dtype=np.float32,
        )

        # Denormalize landmarks to pixel coordinates (if needed)
        landmarks[:, 0] *= face_image.shape[1]  # Scale x-coordinates by image width
        landmarks[:, 1] *= face_image.shape[0]  # Scale y-coordinates by image height

        return landmarks
