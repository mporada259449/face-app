from pathlib import Path
from src_models.models.paths import ModelPaths


def test_model_paths():
    """Test that each ModelPaths enum value is a Path instance."""
    for path in ModelPaths:
        assert isinstance(path.value, Path)
