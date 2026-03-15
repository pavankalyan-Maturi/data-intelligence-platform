import pytest
import requests
import time

BASE_URL = "http://localhost:8000"

def wait_for_server(max_attempts=5):
    """Wait for server to be ready"""
    for i in range(max_attempts):
        try:
            requests.get(f"{BASE_URL}/", timeout=5)
            return True
        except Exception:
            time.sleep(2)
    return False

def test_health():
    """Test API is running"""
    response = requests.get(f"{BASE_URL}/", timeout=10)
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()

def test_upload_endpoint_exists():
    """Test upload endpoint exists"""
    response = requests.post(f"{BASE_URL}/api/upload", timeout=10)
    assert response.status_code == 422

def test_query_endpoint_exists():
    """Test query endpoint exists"""
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"question": "test", "use_agent": False},
        timeout=30
    )
    assert response.status_code in [200, 500]

def test_stats_endpoint():
    """Test stats endpoint exists"""
    response = requests.get(f"{BASE_URL}/api/stats", timeout=10)
    assert response.status_code == 200

def test_files_endpoint():
    """Test files endpoint returns list"""
    response = requests.get(f"{BASE_URL}/api/files", timeout=10)
    assert response.status_code == 200
    assert isinstance(response.json(), list)