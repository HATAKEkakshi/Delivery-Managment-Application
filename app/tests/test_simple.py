import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint without database dependencies"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok server running"}

def test_health_endpoint_method_not_allowed():
    """Test that POST is not allowed on health endpoint"""
    response = client.post("/health")
    assert response.status_code == 405

def test_health_endpoint_response_format():
    """Test the response format of health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert isinstance(data["status"], str)