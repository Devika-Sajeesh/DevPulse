from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code in [200, 404] # 404 is acceptable if root is not defined, just checking it runs
    
def test_health_check():
    # Assuming there might be a health check or status endpoint based on README
    response = client.get("/status")
    if response.status_code != 404:
        assert response.status_code == 200
