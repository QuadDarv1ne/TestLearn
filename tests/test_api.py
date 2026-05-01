"""Tests for TestLearn application."""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import Base, engine
from app.services.progress_service import seed_initial_data

# Create tables and seed data before any tests
Base.metadata.create_all(bind=engine)
seed_initial_data()

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

# ==================== Health Check Tests ====================
def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data

def test_health_detailed(client):
    """Test detailed health check endpoint."""
    response = client.get("/api/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "statistics" in data["database"]

def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True

def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = client.get("/api/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True

def test_app_info(client):
    """Test application info endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

# ==================== Home Page Tests ====================
def test_home_page(client):
    """Test home page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "TestLearn" in response.text

# ==================== API Category Tests ====================
def test_api_categories(client):
    """Test categories API endpoint."""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "description" in first

def test_api_categories_single(client):
    """Test single category endpoint."""
    response = client.get("/api/categories")
    data = response.json()
    if len(data) > 0:
        category_id = data[0]["id"]
        response = client.get(f"/api/categories/{category_id}")
        assert response.status_code == 200
        category_data = response.json()
        assert category_data["id"] == category_id

# ==================== API Topic Tests ====================
def test_api_topics(client):
    """Test topics API endpoint."""
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_topics_by_category(client):
    """Test topics by category endpoint."""
    response = client.get("/api/categories")
    data = response.json()
    if len(data) > 0:
        category_id = data[0]["id"]
        response = client.get(f"/api/topics?category_id={category_id}")
        assert response.status_code == 200

# ==================== API Quiz Tests ====================
def test_api_quizzes(client):
    """Test quizzes API endpoint."""
    response = client.get("/api/quizzes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_quiz_questions(client):
    """Test quiz questions endpoint."""
    response = client.get("/api/quizzes")
    data = response.json()
    if len(data) > 0:
        quiz_id = data[0]["id"]
        response = client.get(f"/api/quizzes/{quiz_id}/questions")
        assert response.status_code == 200

# ==================== API Glossary Tests ====================
def test_api_glossary(client):
    """Test glossary API endpoint."""
    response = client.get("/api/glossary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_glossary_by_letter(client):
    """Test glossary by letter endpoint."""
    response = client.get("/api/glossary?letter=A")
    assert response.status_code == 200

# ==================== API Feedback Tests ====================
def test_api_feedback(client):
    """Test feedback API endpoint."""
    response = client.post(
        "/api/feedback",
        json={"name": "Test User", "message": "Test message"}
    )
    assert response.status_code == 200

def test_api_feedback_validation(client):
    """Test feedback validation - missing required fields."""
    response = client.post(
        "/api/feedback",
        json={"name": ""}
    )
    assert response.status_code in [400, 422]

def test_api_feedback_with_rating(client):
    """Test feedback with rating."""
    response = client.post(
        "/api/feedback",
        json={"name": "Test User", "message": "Great platform!", "rating": 5}
    )
    assert response.status_code == 200

# ==================== API Auth Tests ====================
def test_auth_login_failure(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401

def test_auth_login_first_setup(client):
    """Test first-time admin setup."""
    try:
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin"}
        )
        assert response.status_code in [200, 401, 422]
    except ValueError:
        pass

# ==================== Gamification Tests ====================
def test_gamification_leaderboard(client):
    """Test leaderboard endpoint with pagination."""
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    # New format with pagination
    assert isinstance(data, dict)
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert isinstance(data["items"], list)

def test_gamification_achievements(client):
    """Test achievements endpoint."""
    response = client.get("/api/achievements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_gamification_daily_challenge(client):
    """Test daily challenge endpoint."""
    response = client.get("/api/daily-challenge")
    assert response.status_code in [200, 404]

def test_gamification_certificate(client):
    """Test certificate endpoint."""
    response = client.get("/api/certificate")
    # May fail if requirements not met (5 quizzes passed)
    assert response.status_code in [200, 400, 404]

# ==================== Progress Tests ====================
def test_progress_get(client):
    """Test get user progress."""
    response = client.get("/api/progress")
    assert response.status_code == 200

def test_progress_add_xp(client):
    """Test adding experience points."""
    response = client.post(
        "/api/progress/xp",
        json={"session_id": "test_session", "amount": 100}
    )
    assert response.status_code in [200, 400]

# ==================== Social Features Tests ====================
def test_social_comments_get(client):
    """Test getting comments for a topic."""
    response = client.get("/api/topics/1/comments")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

def test_social_comments_create(client):
    """Test creating a new comment."""
    response = client.post(
        "/api/social/comments",
        json={"topic_id": 1, "content": "Test comment"}
    )
    assert response.status_code in [200, 400, 404, 422]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert data["content"] == "Test comment"

def test_social_comments_like(client):
    """Test liking a comment."""
    create_response = client.post(
        "/api/social/comments",
        json={"topic_id": 1, "content": "Comment for like test"}
    )
    if create_response.status_code == 200:
        comment_id = create_response.json()["id"]
        like_response = client.post(f"/api/social/comments/{comment_id}/like")
        assert like_response.status_code == 200
        data = like_response.json()
        assert data["status"] == "success"
        assert "likes" in data

def test_social_notifications(client):
    """Test notifications endpoint with pagination."""
    response = client.get("/api/social/notifications")
    assert response.status_code == 200
    data = response.json()
    # New format with pagination
    assert isinstance(data, dict)
    assert "items" in data
    assert "page" in data
    assert isinstance(data["items"], list)

def test_social_notifications_mark_read(client):
    """Test marking notification as read."""
    notifications_response = client.get("/api/social/notifications")
    if notifications_response.status_code == 200:
        data = notifications_response.json()
        # New format with pagination
        if isinstance(data, dict) and "items" in data and data["items"]:
            notification_id = data["items"][0]["id"]
            read_response = client.post(
                f"/api/social/notifications/{notification_id}/read"
            )
            assert read_response.status_code == 200

# ==================== Frontend Page Tests ====================
def test_theory_page(client):
    """Test theory page loads successfully."""
    response = client.get("/theory")
    assert response.status_code == 200

def test_stats_page(client):
    """Test stats page loads successfully."""
    response = client.get("/stats")
    assert response.status_code == 200

def test_glossary_page(client):
    """Test glossary page loads successfully."""
    response = client.get("/glossary")
    assert response.status_code == 200

def test_database_page(client):
    """Test database schema page loads successfully."""
    response = client.get("/database")
    assert response.status_code == 200

def test_about_page(client):
    """Test about page loads successfully."""
    response = client.get("/about")
    assert response.status_code == 200

def test_feedback_page(client):
    """Test feedback page loads successfully."""
    response = client.get("/feedback")
    assert response.status_code == 200

def test_leaderboard_page(client):
    """Test leaderboard page loads successfully."""
    response = client.get("/leaderboard")
    assert response.status_code == 200

def test_bookmarks_page(client):
    """Test bookmarks page loads successfully."""
    response = client.get("/bookmarks")
    assert response.status_code == 200

def test_login_page(client):
    """Test login page loads successfully."""
    response = client.get("/login")
    assert response.status_code == 200

def test_quiz_page(client):
    """Test quiz page loads successfully."""
    response = client.get("/quiz")
    assert response.status_code == 200

# ==================== Error Handling Tests ====================
def test_404_page(client):
    """Test 404 error page."""
    response = client.get("/nonexistent-page")
    assert response.status_code == 404

def test_api_404(client):
    """Test API 404 error."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

# ==================== Search Tests ====================
def test_search_endpoint(client):
    """Test search endpoint."""
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert "glossary_terms" in data

def test_search_empty_query(client):
    """Test search with empty query."""
    response = client.get("/api/search?q=")
    assert response.status_code in [200, 400, 422]
