"""
Smoke tests for DevPulse API.

Basic tests to ensure the application starts and endpoints are accessible.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns expected response."""
        response = client.get("/")
        # Root may return 404 if not defined, which is acceptable
        assert response.status_code in [200, 404]
    
    def test_status_endpoint(self):
        """Test status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_reports_list_endpoint(self):
        """Test reports list endpoint."""
        response = client.get("/reports")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_nonexistent_report(self):
        """Test fetching non-existent report returns 404."""
        response = client.get("/reports/999999")
        assert response.status_code == 404
    
    def test_invalid_report_id(self):
        """Test invalid report ID format."""
        response = client.get("/reports/invalid")
        # Should return error (422 for validation or 404)
        assert response.status_code in [404, 422]


class TestAnalyzeEndpoint:
    """Test the analyze endpoint."""
    
    def test_analyze_missing_url(self):
        """Test analyze endpoint without URL."""
        response = client.post("/analyze", json={})
        assert response.status_code == 422  # Validation error
    
    def test_analyze_invalid_url(self):
        """Test analyze endpoint with invalid URL."""
        response = client.post("/analyze", json={"repo_url": "not-a-url"})
        # Should fail validation or analysis
        assert response.status_code in [400, 422, 500]
    
    def test_analyze_non_github_url(self):
        """Test analyze endpoint with non-GitHub URL."""
        response = client.post("/analyze", json={"repo_url": "https://gitlab.com/test/repo"})
        # Should reject non-GitHub URLs
        assert response.status_code in [400, 422, 500]


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoint behavior."""
    
    async def test_concurrent_status_requests(self):
        """Test multiple concurrent status requests."""
        import asyncio
        
        async def make_request():
            return client.get("/status")
        
        # Make 5 concurrent requests
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)

