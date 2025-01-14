import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import User

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
        id=1,
        username='admin',
        password='testpassword',
        is_admin=True
    )
    db_session.add(user)
    yield db_session.query(User).filter_by(id=1).one()
    db_session.query(User).filter_by(id=1).delete()
    db_session.commit()

def test_login_route(client, create_user):
    """Test the login route."""
    response = client.post('/login', data={'username': 'admin', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful' in response.data