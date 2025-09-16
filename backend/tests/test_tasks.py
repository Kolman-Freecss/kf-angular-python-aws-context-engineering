import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import get_db, Base
from main import app
from models.user import User
from models.task import Task, Category
from api.auth import get_password_hash, create_access_token

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

@pytest.fixture
def test_category(db_session, test_user):
    category = Category(
        name="Work",
        color="#3498db",
        user_id=test_user.id
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def test_task(db_session, test_user, test_category):
    task = Task(
        title="Test Task",
        description="Test Description",
        status="todo",
        priority="medium",
        category_id=test_category.id,
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

class TestTaskEndpoints:
    def test_create_task_success(self, client, auth_headers, test_category):
        task_data = {
            "title": "New Task",
            "description": "New Description",
            "status": "todo",
            "priority": "medium",
            "category_id": test_category.id
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "New Description"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["category_id"] == test_category.id
        
    def test_create_task_unauthorized(self, client, test_category):
        task_data = {
            "title": "New Task",
            "description": "New Description",
            "status": "todo",
            "priority": "medium",
            "category_id": test_category.id
        }
        
        response = client.post("/api/tasks", json=task_data)
        
        assert response.status_code == 401
        
    def test_create_task_invalid_data(self, client, auth_headers):
        task_data = {
            "title": "",  # Empty title should fail
            "description": "New Description",
            "status": "todo",
            "priority": "medium"
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 422
        
    def test_get_tasks_success(self, client, auth_headers, test_task):
        response = client.get("/api/tasks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"
        
    def test_get_tasks_with_filters(self, client, auth_headers, test_task):
        response = client.get("/api/tasks?status=todo&priority=medium", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        
    def test_get_tasks_empty_filters(self, client, auth_headers, test_task):
        response = client.get("/api/tasks?status=done", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 0
        
    def test_get_task_by_id_success(self, client, auth_headers, test_task):
        response = client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == "Test Task"
        
    def test_get_task_by_id_not_found(self, client, auth_headers):
        response = client.get("/api/tasks/999", headers=auth_headers)
        
        assert response.status_code == 404
        
    def test_get_task_by_id_unauthorized(self, client, test_task):
        response = client.get(f"/api/tasks/{test_task.id}")
        
        assert response.status_code == 401
        
    def test_update_task_success(self, client, auth_headers, test_task):
        update_data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": "in_progress",
            "priority": "high"
        }
        
        response = client.put(f"/api/tasks/{test_task.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated Description"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"
        
    def test_update_task_not_found(self, client, auth_headers):
        update_data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": "in_progress",
            "priority": "high"
        }
        
        response = client.put("/api/tasks/999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        
    def test_delete_task_success(self, client, auth_headers, test_task):
        response = client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
    def test_delete_task_not_found(self, client, auth_headers):
        response = client.delete("/api/tasks/999", headers=auth_headers)
        
        assert response.status_code == 404
        
    def test_get_task_analytics_success(self, client, auth_headers, test_task):
        response = client.get("/api/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "pending_tasks" in data
        assert "in_progress_tasks" in data
        assert "completion_rate" in data
        assert "tasks_by_priority" in data
        assert "tasks_by_category" in data

class TestCategoryEndpoints:
    def test_create_category_success(self, client, auth_headers):
        category_data = {
            "name": "Personal",
            "color": "#e74c3c"
        }
        
        response = client.post("/api/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Personal"
        assert data["color"] == "#e74c3c"
        
    def test_create_category_duplicate_name(self, client, auth_headers, test_category):
        category_data = {
            "name": "Work",  # Same name as test_category
            "color": "#e74c3c"
        }
        
        response = client.post("/api/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "category with this name already exists" in response.json()["detail"].lower()
        
    def test_get_categories_success(self, client, auth_headers, test_category):
        response = client.get("/api/categories", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Work"
        
    def test_update_category_success(self, client, auth_headers, test_category):
        update_data = {
            "name": "Updated Work",
            "color": "#2ecc71"
        }
        
        response = client.put(f"/api/categories/{test_category.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Work"
        assert data["color"] == "#2ecc71"
        
    def test_delete_category_success(self, client, auth_headers, test_category):
        response = client.delete(f"/api/categories/{test_category.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
    def test_delete_category_with_tasks(self, client, auth_headers, test_category, test_task):
        response = client.delete(f"/api/categories/{test_category.id}", headers=auth_headers)
        
        assert response.status_code == 400
        assert "cannot delete category with existing tasks" in response.json()["detail"].lower()

class TestTaskValidation:
    def test_task_status_validation(self, client, auth_headers, test_category):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": "invalid_status",  # Invalid status
            "priority": "medium",
            "category_id": test_category.id
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 422
        
    def test_task_priority_validation(self, client, auth_headers, test_category):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "invalid_priority",  # Invalid priority
            "category_id": test_category.id
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 422
        
    def test_task_category_validation(self, client, auth_headers):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "category_id": 999  # Non-existent category
        }
        
        response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "category not found" in response.json()["detail"].lower()

class TestTaskPagination:
    def test_task_pagination(self, client, auth_headers, test_category, db_session, test_user):
        # Create multiple tasks
        for i in range(15):
            task = Task(
                title=f"Task {i}",
                description=f"Description {i}",
                status="todo",
                priority="medium",
                category_id=test_category.id,
                user_id=test_user.id
            )
            db_session.add(task)
        db_session.commit()
        
        # Test first page
        response = client.get("/api/tasks?page=1&per_page=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 10
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert data["total"] == 15
        
        # Test second page
        response = client.get("/api/tasks?page=2&per_page=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 5
        assert data["page"] == 2
