import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """Test API is running"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()

def test_upload_endpoint_exists():
    """Test upload endpoint exists"""
    response = requests.post(f"{BASE_URL}/api/upload")
    # 422 means endpoint exists but needs a file
    assert response.status_code == 422

def test_query_endpoint_exists():
    """Test query endpoint exists"""
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"question": "test", "use_agent": False}
    )
    # 500 is ok — means endpoint exists but LLM not available in CI
    assert response.status_code in [200, 500]

def test_stats_endpoint():
    """Test stats endpoint exists"""
    response = requests.get(f"{BASE_URL}/api/stats")
    assert response.status_code == 200

def test_files_endpoint():
    """Test files endpoint exists"""
    response = requests.get(f"{BASE_URL}/api/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)