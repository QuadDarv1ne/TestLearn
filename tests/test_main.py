"""Tests for TestLearn application."""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_home_page(client):
    """Test home page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "TestLearn" in response.text

def test_api_categories(client):
    """Test categories API endpoint."""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # We expect at least one category from the seed data
    assert len(data) > 0
    # Check structure of first category
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "description" in first

def test_api_quizzes(client):
    """Test quizzes API endpoint."""
    response = client.get("/api/quizzes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_glossary(client):
    """Test glossary API endpoint."""
    response = client.get("/api/glossary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_feedback(client):
    """Test feedback API endpoint."""
    response = client.post(
        "/api/feedback",
        json={"name": "Test User", "message": "Test message"}
    )
    assert response.status_code == 200

def test_auth_login_failure(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401

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

def test_api_topics(client):
    """Test topics API endpoint."""
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_feedback_validation(client):
    """Test feedback validation - missing required fields."""
    response = client.post(
        "/api/feedback",
        json={"name": ""}  # Missing message
    )
    # Should return validation error
    assert response.status_code in [400, 422]
