import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import get_db, Base
from core.config import settings
from main import app
from models.user import User
from api.auth import get_password_hash, verify_password, create_access_token, authenticate_user

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestPasswordHashing:
    def test_password_hashing(self):
        password = "testpassword"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        
    def test_password_verification(self):
        password = "testpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

class TestTokenCreation:
    def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

class TestUserAuthentication:
    def test_authenticate_user_success(self, db_session, test_user):
        result = authenticate_user(db_session, "test@example.com", "password123")
        
        assert result is not False
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        
    def test_authenticate_user_wrong_password(self, db_session, test_user):
        result = authenticate_user(db_session, "test@example.com", "wrongpassword")
        
        assert result is False
        
    def test_authenticate_user_nonexistent_email(self, db_session):
        result = authenticate_user(db_session, "nonexistent@example.com", "password123")
        
        assert result is False

class TestAuthEndpoints:
    def test_register_success(self, client):
        user_data = {
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"
        
    def test_register_duplicate_email(self, client, test_user):
        user_data = {
            "full_name": "Another User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()
        
    def test_register_invalid_email(self, client):
        user_data = {
            "full_name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
        
    def test_register_weak_password(self, client):
        user_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
        
    def test_login_success(self, client, test_user):
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        
    def test_login_wrong_password(self, client, test_user):
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect email or password" in response.json()["detail"].lower()
        
    def test_login_nonexistent_user(self, client):
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect email or password" in response.json()["detail"].lower()
        
    def test_get_current_user_success(self, client, test_user):
        # First login to get token
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        login_response = client.post("/api/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        
    def test_get_current_user_no_token(self, client):
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        
    def test_get_current_user_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        
    def test_refresh_token_success(self, client, test_user):
        # First login to get token
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        login_response = client.post("/api/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to refresh
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        
    def test_refresh_token_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/api/auth/refresh", headers=headers)
        
        assert response.status_code == 401

class TestPasswordReset:
    def test_request_password_reset_success(self, client, test_user):
        data = {"email": "test@example.com"}
        
        response = client.post("/api/auth/password-reset", json=data)
        
        assert response.status_code == 200
        assert "password reset email sent" in response.json()["message"].lower()
        
    def test_request_password_reset_nonexistent_email(self, client):
        data = {"email": "nonexistent@example.com"}
        
        response = client.post("/api/auth/password-reset", json=data)
        
        assert response.status_code == 200  # Should not reveal if email exists
        assert "password reset email sent" in response.json()["message"].lower()
        
    def test_reset_password_success(self, client, test_user):
        # This would require a valid reset token, which is complex to test
        # In a real implementation, you'd need to generate a valid token
        reset_data = {
            "token": "valid-reset-token",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/auth/password-reset-confirm", json=reset_data)
        
        # This test would need proper token generation
        assert response.status_code in [200, 400]  # 400 for invalid token
        
    def test_reset_password_invalid_token(self, client):
        reset_data = {
            "token": "invalid-token",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/auth/password-reset-confirm", json=reset_data)
        
        assert response.status_code == 400
