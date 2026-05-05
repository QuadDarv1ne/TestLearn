from fastapi.testclient import TestClient
from main import app

def test_rate_limit_endpoint():
    """Test the rate limit endpoint exists and works."""
    client = TestClient(app)
    response = client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Rate limiting is working"}

if __name__ == "__main__":
    test_rate_limit_endpoint()
    print("Rate limit endpoint test passed!")