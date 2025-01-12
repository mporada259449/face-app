import cv2
import numpy as np
import onnxruntime
from typing import Tuple
from .paths import ModelPaths

class FaceEmbedderBackbone:
    """
    A class representing the FaceEmbedder model for extracting facial embeddings.
    """

    def __init__(self, model_path: str = ModelPaths.FACE_EMBEDDER.value):
        """
        Initialize the FaceEmbedder backbone.

        Parameters:
        - model_path (str): Path to the ONNX model file.
        """
        self.model_path: str = model_path
        self.session: onnxruntime.InferenceSession = onnxruntime.InferenceSession(model_path)
        self.input_name: str = self.session.get_inputs()[0].name

    def forward(self, image: np.ndarray) -> np.ndarray:
        """
        Perform a forward pass to extract embeddings from an image.

        Parameters:
        - image (np.ndarray): Preprocessed input image as a NumPy array.

        Returns:
        - np.ndarray: Embeddings extracted from the image.
        """
        embeddings: np.ndarray = self.session.run(None, {self.input_name: image})[0]
        return embeddings


class SiameseNetwork:
    """
    A class representing a Siamese network using the FaceEmbedder backbone.
    """

    def __init__(self, face_embedder_backbone: FaceEmbedderBackbone):
        """
        Initialize the Siamese network.

        Parameters:
        - face_embedder_backbone (FaceEmbedderBackbone): An instance of the FaceEmbedder backbone.
        """
        self.face_embedder_backbone: FaceEmbedderBackbone = face_embedder_backbone

    def forward(self, image1: np.ndarray, image2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform a forward pass for the Siamese network.

        Parameters:
        - image1 (np.ndarray): First preprocessed input image.
        - image2 (np.ndarray): Second preprocessed input image.

        Returns:
        - Tuple[np.ndarray, np.ndarray]: Embeddings for both input images.
        """
        embedding1: np.ndarray = self.face_embedder_backbone.forward(image1)
        embedding2: np.ndarray = self.face_embedder_backbone.forward(image2)
        return embedding1, embedding2


def preprocess_image_direct(image: np.ndarray) -> np.ndarray:
    """
    Preprocess a NumPy image directly for the FaceEmbedder model.

    Parameters:
    - image (np.ndarray): Input image (H, W, C) in RGB format.

    Returns:
    - np.ndarray: Preprocessed image suitable for FaceVerifier input.
    """
    # Resize to 112x112
    resized_image: np.ndarray = cv2.resize(image, (112, 112))

    # Normalize to [-1, 1]
    normalized_image: np.ndarray = (resized_image - 127.5) / 128.0

    # Convert to CHW format (C, H, W)
    chw_image: np.ndarray = np.transpose(normalized_image, (2, 0, 1))

    # Add batch dimension and convert to float32
    input_tensor: np.ndarray = np.expand_dims(chw_image, axis=0).astype(np.float32)

    return input_tensor