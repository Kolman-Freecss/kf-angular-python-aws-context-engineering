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
import time

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
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

class TestUserWorkflow:
    """Test complete user workflows from registration to task management"""
    
    def test_complete_user_registration_and_task_workflow(self, client):
        """Test complete workflow: register -> login -> create category -> create task -> manage task"""
        
        # 1. Register new user
        user_data = {
            "full_name": "Workflow User",
            "email": "workflow@example.com",
            "password": "password123"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert "access_token" in register_data
        
        # 2. Use token to access protected endpoints
        token = register_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create a category
        category_data = {
            "name": "Work",
            "color": "#3498db"
        }
        
        category_response = client.post("/api/categories", json=category_data, headers=headers)
        assert category_response.status_code == 200
        category = category_response.json()
        assert category["name"] == "Work"
        
        # 4. Create a task
        task_data = {
            "title": "Complete project",
            "description": "Finish the project by end of week",
            "status": "todo",
            "priority": "high",
            "category_id": category["id"]
        }
        
        task_response = client.post("/api/tasks", json=task_data, headers=headers)
        assert task_response.status_code == 200
        task = task_response.json()
        assert task["title"] == "Complete project"
        assert task["category_id"] == category["id"]
        
        # 5. Update task status
        update_data = {
            "status": "in_progress",
            "priority": "high"
        }
        
        update_response = client.put(f"/api/tasks/{task['id']}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["status"] == "in_progress"
        
        # 6. Get task analytics
        analytics_response = client.get("/api/tasks/analytics", headers=headers)
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert analytics["total_tasks"] == 1
        assert analytics["in_progress_tasks"] == 1
        
        # 7. Complete task
        complete_data = {
            "status": "done",
            "priority": "high"
        }
        
        complete_response = client.put(f"/api/tasks/{task['id']}", json=complete_data, headers=headers)
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["status"] == "done"
        
        # 8. Verify analytics updated
        analytics_response = client.get("/api/tasks/analytics", headers=headers)
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert analytics["completed_tasks"] == 1
        assert analytics["completion_rate"] == 100
        
        # 9. Delete task
        delete_response = client.delete(f"/api/tasks/{task['id']}", headers=headers)
        assert delete_response.status_code == 200
        
        # 10. Verify task is deleted
        get_response = client.get(f"/api/tasks/{task['id']}", headers=headers)
        assert get_response.status_code == 404

class TestConcurrentOperations:
    """Test concurrent operations and data consistency"""
    
    def test_concurrent_task_creation(self, client, auth_headers, test_user, db_session):
        """Test creating multiple tasks concurrently"""
        
        # Create a category first
        category_data = {
            "name": "Concurrent Test",
            "color": "#e74c3c"
        }
        
        category_response = client.post("/api/categories", json=category_data, headers=auth_headers)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create multiple tasks
        tasks_created = []
        for i in range(5):
            task_data = {
                "title": f"Concurrent Task {i}",
                "description": f"Description for task {i}",
                "status": "todo",
                "priority": "medium",
                "category_id": category["id"]
            }
            
            response = client.post("/api/tasks", json=task_data, headers=auth_headers)
            assert response.status_code == 200
            tasks_created.append(response.json())
        
        # Verify all tasks were created
        get_tasks_response = client.get("/api/tasks", headers=auth_headers)
        assert get_tasks_response.status_code == 200
        tasks_data = get_tasks_response.json()
        assert len(tasks_data["tasks"]) == 5
        
        # Verify each task has unique ID
        task_ids = [task["id"] for task in tasks_data["tasks"]]
        assert len(set(task_ids)) == 5  # All IDs should be unique

class TestDataConsistency:
    """Test data consistency and relationships"""
    
    def test_category_task_relationship(self, client, auth_headers, test_user, db_session):
        """Test that tasks are properly linked to categories"""
        
        # Create category
        category_data = {
            "name": "Relationship Test",
            "color": "#2ecc71"
        }
        
        category_response = client.post("/api/categories", json=category_data, headers=auth_headers)
        category = category_response.json()
        
        # Create task with category
        task_data = {
            "title": "Relationship Task",
            "description": "Test relationship",
            "status": "todo",
            "priority": "medium",
            "category_id": category["id"]
        }
        
        task_response = client.post("/api/tasks", json=task_data, headers=auth_headers)
        task = task_response.json()
        
        # Verify relationship
        assert task["category_id"] == category["id"]
        
        # Get task and verify category info
        get_task_response = client.get(f"/api/tasks/{task['id']}", headers=auth_headers)
        retrieved_task = get_task_response.json()
        assert retrieved_task["category_id"] == category["id"]
        
        # Try to delete category with tasks (should fail)
        delete_category_response = client.delete(f"/api/categories/{category['id']}", headers=auth_headers)
        assert delete_category_response.status_code == 400
        
        # Delete task first
        delete_task_response = client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)
        assert delete_task_response.status_code == 200
        
        # Now delete category should work
        delete_category_response = client.delete(f"/api/categories/{category['id']}", headers=auth_headers)
        assert delete_category_response.status_code == 200

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_token_handling(self, client):
        """Test handling of invalid tokens"""
        
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        
        # Try to access protected endpoint
        response = client.get("/api/tasks", headers=invalid_headers)
        assert response.status_code == 401
        
        # Try to create task
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium"
        }
        
        response = client.post("/api/tasks", json=task_data, headers=invalid_headers)
        assert response.status_code == 401
    
    def test_malformed_request_handling(self, client, auth_headers):
        """Test handling of malformed requests"""
        
        # Missing required fields
        malformed_data = {
            "title": "Test Task"
            # Missing other required fields
        }
        
        response = client.post("/api/tasks", json=malformed_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Invalid JSON
        response = client.post(
            "/api/tasks",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_nonexistent_resource_handling(self, client, auth_headers):
        """Test handling of requests for nonexistent resources"""
        
        # Get nonexistent task
        response = client.get("/api/tasks/999999", headers=auth_headers)
        assert response.status_code == 404
        
        # Update nonexistent task
        update_data = {"title": "Updated Task"}
        response = client.put("/api/tasks/999999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        
        # Delete nonexistent task
        response = client.delete("/api/tasks/999999", headers=auth_headers)
        assert response.status_code == 404

class TestPerformance:
    """Test performance characteristics"""
    
    def test_bulk_task_creation_performance(self, client, auth_headers, test_user, db_session):
        """Test performance of creating many tasks"""
        
        # Create category
        category_data = {
            "name": "Performance Test",
            "color": "#9b59b6"
        }
        
        category_response = client.post("/api/categories", json=category_data, headers=auth_headers)
        category = category_response.json()
        
        # Measure time for creating multiple tasks
        start_time = time.time()
        
        tasks_created = []
        for i in range(50):  # Create 50 tasks
            task_data = {
                "title": f"Performance Task {i}",
                "description": f"Description for performance test task {i}",
                "status": "todo",
                "priority": "medium",
                "category_id": category["id"]
            }
            
            response = client.post("/api/tasks", json=task_data, headers=auth_headers)
            assert response.status_code == 200
            tasks_created.append(response.json())
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert creation_time < 10.0  # 10 seconds for 50 tasks
        
        # Verify all tasks were created
        get_tasks_response = client.get("/api/tasks", headers=auth_headers)
        assert get_tasks_response.status_code == 200
        tasks_data = get_tasks_response.json()
        assert len(tasks_data["tasks"]) == 50
    
    def test_pagination_performance(self, client, auth_headers, test_user, db_session):
        """Test performance of pagination with large datasets"""
        
        # Create category
        category_data = {
            "name": "Pagination Test",
            "color": "#f39c12"
        }
        
        category_response = client.post("/api/categories", json=category_data, headers=auth_headers)
        category = category_response.json()
        
        # Create many tasks
        for i in range(100):
            task = Task(
                title=f"Pagination Task {i}",
                description=f"Description for pagination test task {i}",
                status="todo",
                priority="medium",
                category_id=category["id"],
                user_id=test_user.id
            )
            db_session.add(task)
        db_session.commit()
        
        # Test pagination performance
        start_time = time.time()
        
        response = client.get("/api/tasks?page=1&per_page=20", headers=auth_headers)
        assert response.status_code == 200
        
        end_time = time.time()
        pagination_time = end_time - start_time
        
        # Should be fast even with large dataset
        assert pagination_time < 1.0  # 1 second for pagination
        
        data = response.json()
        assert len(data["tasks"]) == 20
        assert data["total"] == 100
