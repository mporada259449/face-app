import pytest
from app import create_app, db
from app.models import User
from app.config import TestConfig

@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

def test_user_model(app):
    """Test the User model."""
    with app.app_context():
        user = User(username='testuser', password='testpassword', is_admin=False)
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.password == 'testpassword'
        assert user.is_admin is False

        # Cover the missing line
        user_from_db = User.query.filter_by(username='testuser').first()
        assert user_from_db is not None
        assert user_from_db.username == 'testuser'