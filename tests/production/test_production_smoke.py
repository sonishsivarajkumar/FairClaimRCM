"""
Production smoke tests - minimal tests to verify production deployment
"""

import pytest
import requests
import os


class TestProductionSmoke:
    """Minimal smoke tests for production environment."""
    
    @pytest.fixture
    def production_url(self):
        """Get production URL from environment."""
        return os.getenv("PRODUCTION_URL", "https://fairclaimrcm.example.com")
    
    @pytest.fixture
    def api_key(self):
        """Get API key for production."""
        return os.getenv("API_KEY")
    
    @pytest.fixture
    def headers(self, api_key):
        """Headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
    
    def test_health_check(self, production_url):
        """Test basic health check."""
        response = requests.get(f"{production_url}/health", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_health_check(self, production_url, headers):
        """Test API health check."""
        response = requests.get(
            f"{production_url}/api/v1/health", 
            headers=headers, 
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_basic_validation(self, production_url, headers):
        """Test basic code validation works."""
        # Test well-known valid codes
        response = requests.get(
            f"{production_url}/api/v1/terminology/icd10/validate/E11.9",
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["code"] == "E11.9"
    
    def test_search_basic(self, production_url, headers):
        """Test basic search functionality."""
        response = requests.get(
            f"{production_url}/api/v1/terminology/icd10/search",
            params={"query": "diabetes", "limit": 5},
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "codes" in data
        assert isinstance(data["codes"], list)
    
    def test_error_handling(self, production_url, headers):
        """Test that error handling works properly."""
        # Test invalid endpoint
        response = requests.get(
            f"{production_url}/api/v1/nonexistent",
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 404
    
    def test_security_headers(self, production_url):
        """Test that security headers are present."""
        response = requests.get(f"{production_url}/health", timeout=30)
        
        # Check for common security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        # Add more security header checks as needed
