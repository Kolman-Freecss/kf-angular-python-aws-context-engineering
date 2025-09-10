import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import get_db, Base
from main import app
from models.user import User
from models.task import Task, Category
from api.auth import get_password_hash, create_access_token
import concurrent.futures

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
        email="perf@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Performance Test User",
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

@pytest.fixture
def test_data(db_session, test_user):
    """Create test data for performance testing"""
    
    # Create categories
    categories = []
    for i in range(5):
        category = Category(
            name=f"Category {i}",
            color=f"#3498db",
            user_id=test_user.id
        )
        db_session.add(category)
        categories.append(category)
    
    db_session.commit()
    
    # Create tasks
    tasks = []
    for i in range(100):
        task = Task(
            title=f"Performance Task {i}",
            description=f"Description for performance test task {i}",
            status="todo" if i % 3 == 0 else "in_progress" if i % 3 == 1 else "done",
            priority="low" if i % 4 == 0 else "medium" if i % 4 == 1 else "high" if i % 4 == 2 else "urgent",
            category_id=categories[i % 5].id,
            user_id=test_user.id
        )
        db_session.add(task)
        tasks.append(task)
    
    db_session.commit()
    return {"categories": categories, "tasks": tasks}

class TestAPIPerformance:
    """Test API performance characteristics"""
    
    def test_task_list_performance(self, client, auth_headers, test_data):
        """Test task list endpoint performance"""
        
        start_time = time.time()
        
        response = client.get("/api/tasks?page=1&per_page=20", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5  # Should respond within 500ms
        
        data = response.json()
        assert len(data["tasks"]) == 20
        assert data["total"] == 100
    
    def test_task_search_performance(self, client, auth_headers, test_data):
        """Test task search performance"""
        
        start_time = time.time()
        
        response = client.get("/api/tasks?page=1&per_page=10&status=todo", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.3  # Filtered search should be fast
        
        data = response.json()
        assert all(task["status"] == "todo" for task in data["tasks"])
    
    def test_cached_endpoints_performance(self, client, auth_headers, test_data):
        """Test cached endpoints performance"""
        
        # First request (cache miss)
        start_time = time.time()
        response1 = client.get("/api/cached/tasks?page=1&per_page=20", headers=auth_headers)
        first_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = client.get("/api/cached/tasks?page=1&per_page=20", headers=auth_headers)
        second_request_time = time.time() - start_time
        
        assert response2.status_code == 200
        
        # Cache hit should be significantly faster
        assert second_request_time < first_request_time * 0.5
        
        # Responses should be identical
        assert response1.json() == response2.json()
    
    def test_concurrent_requests_performance(self, client, auth_headers, test_data):
        """Test performance under concurrent load"""
        
        def make_request():
            response = client.get("/api/tasks?page=1&per_page=10", headers=auth_headers)
            return response.status_code == 200
        
        # Make 10 concurrent requests
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        assert all(results)
        
        # Should handle concurrent requests efficiently
        assert total_time < 2.0  # 10 requests in under 2 seconds
        
        # Average response time should be reasonable
        avg_response_time = total_time / 10
        assert avg_response_time < 0.5
    
    def test_analytics_performance(self, client, auth_headers, test_data):
        """Test analytics endpoint performance"""
        
        start_time = time.time()
        
        response = client.get("/api/tasks/analytics", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Analytics should be computed within 1 second
        
        data = response.json()
        assert data["total_tasks"] == 100
        assert "completion_rate" in data
        assert "tasks_by_priority" in data
        assert "tasks_by_category" in data
    
    def test_pagination_performance(self, client, auth_headers, test_data):
        """Test pagination performance with large datasets"""
        
        # Test different page sizes
        page_sizes = [10, 20, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            
            response = client.get(f"/api/tasks?page=1&per_page={page_size}", headers=auth_headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 0.5  # Should be fast regardless of page size
            
            data = response.json()
            assert len(data["tasks"]) == page_size
    
    def test_memory_usage_performance(self, client, auth_headers, test_data):
        """Test memory usage during operations"""
        
        # Make multiple requests and check for memory leaks
        for i in range(20):
            response = client.get(f"/api/tasks?page={i % 5 + 1}&per_page=20", headers=auth_headers)
            assert response.status_code == 200
        
        # Memory usage should remain stable
        # This is a basic test - in production you'd use more sophisticated memory monitoring
        assert True  # Placeholder for memory usage validation

class TestDatabasePerformance:
    """Test database query performance"""
    
    def test_query_optimization(self, client, auth_headers, test_data):
        """Test that queries are optimized"""
        
        # Test with different filter combinations
        filter_combinations = [
            {},
            {"status": "todo"},
            {"priority": "high"},
            {"status": "todo", "priority": "high"},
            {"category_id": test_data["categories"][0].id}
        ]
        
        for filters in filter_combinations:
            start_time = time.time()
            
            params = "&".join([f"{k}={v}" for k, v in filters.items()])
            url = f"/api/tasks?page=1&per_page=20"
            if params:
                url += f"&{params}"
            
            response = client.get(url, headers=auth_headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 0.5  # All queries should be fast
            
            data = response.json()
            assert len(data["tasks"]) <= 20
    
    def test_bulk_operations_performance(self, client, auth_headers, test_data):
        """Test bulk operations performance"""
        
        # Create multiple tasks quickly
        start_time = time.time()
        
        created_tasks = []
        for i in range(10):
            task_data = {
                "title": f"Bulk Task {i}",
                "description": f"Bulk description {i}",
                "status": "todo",
                "priority": "medium",
                "category_id": test_data["categories"][0].id
            }
            
            response = client.post("/api/tasks", json=task_data, headers=auth_headers)
            assert response.status_code == 200
            created_tasks.append(response.json())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should create 10 tasks quickly
        assert total_time < 2.0
        
        # Clean up
        for task in created_tasks:
            client.delete(f"/api/tasks/{task['id']}", headers=auth_headers)

class TestCachePerformance:
    """Test caching performance"""
    
    def test_cache_hit_ratio(self, client, auth_headers, test_data):
        """Test cache hit ratio"""
        
        # Make multiple identical requests
        requests_made = 10
        cache_hits = 0
        
        for i in range(requests_made):
            start_time = time.time()
            response = client.get("/api/cached/tasks?page=1&per_page=20", headers=auth_headers)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            
            # First request should be slower (cache miss), subsequent should be faster (cache hit)
            if i == 0:
                # First request - cache miss
                assert response_time > 0.1
            else:
                # Subsequent requests - cache hits
                if response_time < 0.05:  # Very fast response indicates cache hit
                    cache_hits += 1
        
        # Should have good cache hit ratio
        cache_hit_ratio = cache_hits / (requests_made - 1)
        assert cache_hit_ratio > 0.8  # At least 80% cache hit ratio
    
    def test_cache_invalidation(self, client, auth_headers, test_data):
        """Test cache invalidation performance"""
        
        # Get initial cached data
        response1 = client.get("/api/cached/tasks?page=1&per_page=20", headers=auth_headers)
        assert response1.status_code == 200
        initial_data = response1.json()
        
        # Create new task (should invalidate cache)
        task_data = {
            "title": "Cache Invalidation Test",
            "description": "Test cache invalidation",
            "status": "todo",
            "priority": "medium",
            "category_id": test_data["categories"][0].id
        }
        
        create_response = client.post("/api/cached/tasks", json=task_data, headers=auth_headers)
        assert create_response.status_code == 200
        
        # Get data again (should reflect new task)
        response2 = client.get("/api/cached/tasks?page=1&per_page=20", headers=auth_headers)
        assert response2.status_code == 200
        updated_data = response2.json()
        
        # Should have one more task
        assert updated_data["total"] == initial_data["total"] + 1
        
        # Clean up
        client.delete(f"/api/cached/tasks/{create_response.json()['id']}", headers=auth_headers)

class TestPerformanceMonitoring:
    """Test performance monitoring endpoints"""
    
    def test_performance_stats_endpoint(self, client, auth_headers, test_data):
        """Test performance statistics endpoint"""
        
        # Make some requests to generate stats
        for i in range(5):
            client.get("/api/tasks?page=1&per_page=10", headers=auth_headers)
        
        # Get performance stats
        response = client.get("/performance/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert "api_performance" in stats
        assert "database_performance" in stats
        
        api_stats = stats["api_performance"]
        assert "request_count" in api_stats
        assert "average_response_time" in api_stats
        assert "slow_requests" in api_stats
        
        db_stats = stats["database_performance"]
        assert "total_queries" in db_stats
        assert "average_query_time" in db_stats
    
    def test_performance_reset_endpoint(self, client, auth_headers, test_data):
        """Test performance statistics reset"""
        
        # Make some requests
        client.get("/api/tasks?page=1&per_page=10", headers=auth_headers)
        
        # Reset stats
        response = client.post("/performance/reset")
        assert response.status_code == 200
        
        # Check that stats are reset
        stats_response = client.get("/performance/stats")
        stats = stats_response.json()
        
        assert stats["api_performance"]["request_count"] == 0
        assert stats["database_performance"]["total_queries"] == 0
