import numpy as np
import pytest
from src_models.models.face_verifier import (
    FaceEmbedderBackbone,
    SiameseNetwork,
    preprocess_image_direct,
)


# Dummy session to simulate ONNX runtime behavior
class DummySession:
    def __init__(self, output):
        self._output = output

    def get_inputs(self):
        class DummyInput:
            name = "input"

        return [DummyInput()]

    def run(self, _, inputs):
        return [self._output]


@pytest.fixture
def face_embedder():
    """Return a FaceEmbedderBackbone instance with a dummy session."""
    dummy_output = np.array([1, 2, 3])
    embedder = FaceEmbedderBackbone.__new__(FaceEmbedderBackbone)
    embedder.session = DummySession(dummy_output)
    embedder.input_name = "input"
    return embedder


def test_face_embedder_forward(face_embedder):
    """Test the forward pass of the face embedder."""
    dummy_input = np.ones((1, 3, 112, 112), dtype=np.float32)
    output = face_embedder.forward(dummy_input)
    np.testing.assert_array_equal(output, np.array([1, 2, 3]))


def test_siamese_network_forward(face_embedder):
    """Test the Siamese network's forward method."""
    siamese = SiameseNetwork(face_embedder)
    image1 = np.ones((1, 3, 112, 112), dtype=np.float32)
    image2 = np.ones((1, 3, 112, 112), dtype=np.float32)
    emb1, emb2 = siamese.forward(image1, image2)
    np.testing.assert_array_equal(emb1, np.array([1, 2, 3]))
    np.testing.assert_array_equal(emb2, np.array([1, 2, 3]))


def test_preprocess_image_direct():
    """Test that preprocess_image_direct returns the correct shape and type."""
    dummy_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    preprocessed = preprocess_image_direct(dummy_image)
    assert preprocessed.shape == (1, 3, 112, 112)
    assert preprocessed.dtype == np.float32
