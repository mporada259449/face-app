import pytest
from app import create_app
from app.config import TestConfig

def test_create_app():
    """Test the create_app function."""
    app = create_app(TestConfig)
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == TestConfig.SQLALCHEMY_DATABASE_URI