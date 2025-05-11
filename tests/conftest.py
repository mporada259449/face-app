import pytest
from app import create_app, db
from app.models import User
from app.config import TestConfig

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        session = db.session
        yield session
        session.rollback()
        session.remove()

@pytest.fixture
def create_user(db_session):
    user = User(
        username='admin',
        password='testpassword',
        is_admin=True,
    )
    db_session.add(user)
    yield db_session.query(User).filter_by(id=1).one()
    db_session.query(User).filter_by(id=1).delete()
    db_session.commit()



def test_app_context(app):
    """Test the app context setup and teardown."""
    with app.app_context():
        assert db.engine.url.database == TestConfig.SQLALCHEMY_DATABASE_URI

def test_client_context(client):
    """Test the client context setup."""
    response = client.get('/')
    assert response.status_code == 404  # Assuming the root route is not defined