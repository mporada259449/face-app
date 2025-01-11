import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Any, Tuple, Optional
from .paths import ModelPaths


class FaceDetector:
    """
    A class to detect faces in an image using MediaPipe's Face Detection Task.
    """

    def __init__(
        self,
        model_path: str = ModelPaths.FACE_DETECTOR.value,
        device: str = "cpu",
        margin: float = 0.15,
        vertical_shift_percentage: float = 0.1,
    ):
        """
        Initialize the FaceDetector with a MediaPipe model.

        Parameters:
        - model_path (str): Path to the MediaPipe model file.
        - device (str): Device to run the model on ("cpu" or "cuda").
        - margin (float): Fractional padding around the bounding box.
        - vertical_shift_percentage (float): Fractional shift of the cropped region upward.
        """
        self.model_path: str = model_path
        self.device: str = device
        self.margin: float = margin
        self.vertical_shift_percentage: float = vertical_shift_percentage
        self.face_detector: Any = self._load_model()

    def _load_model(self) -> Any:
        """
        Load the MediaPipe Face Detection model.

        Returns:
        - Any: The loaded face detection model.
        """
        # Set the appropriate device delegate (GPU or CPU)
        delegate_device = (
            python.BaseOptions.Delegate.GPU
            if self.device == "cuda"
            else python.BaseOptions.Delegate.CPU
        )
        base_options = python.BaseOptions(
            model_asset_path=self.model_path, delegate=delegate_device
        )
        options = vision.FaceDetectorOptions(base_options=base_options)
        return vision.FaceDetector.create_from_options(options)

    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the first face in the input image.

        Parameters:
        - image (np.ndarray): Input image (RGB format) as a NumPy array.

        Returns:
        - Optional[Tuple[int, int, int, int]]: Bounding box (x, y, width, height) of the first detected face,
                                               or None if no face is detected.
        """
        # Convert the image to MediaPipe's required format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        # Run face detection
        detection_result = self.face_detector.detect(mp_image)
        if not detection_result.detections:
            return None  # No faces detected

        # Extract bounding box for the first detected face
        bbox = detection_result.detections[0].bounding_box
        return int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)

    def crop_face(
        self, image: np.ndarray, face_coords: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Crop a face from the image based on bounding box coordinates with optional padding.

        Parameters:
        - image (np.ndarray): The original image (RGB format) as a NumPy array.
        - face_coords (Tuple[int, int, int, int]): Bounding box coordinates (x, y, width, height).

        Returns:
        - np.ndarray: The cropped face with padding applied.
        """
        x, y, w, h = face_coords
        height, width = image.shape[:2]

        # Apply vertical shift (upward shift)
        vertical_shift_pixels = int(h * self.vertical_shift_percentage)
        y = max(y - vertical_shift_pixels, 0)

        # Calculate padding
        x_margin = int(w * self.margin)
        y_margin = int(h * self.margin)

        # Adjust coordinates with padding
        x_start = max(x - x_margin, 0)
        y_start = max(y - y_margin, 0)
        x_end = min(x + w + x_margin, width)
        y_end = min(y + h + y_margin, height)

        # Crop and return the face region
        return image[y_start:y_end, x_start:x_end]
