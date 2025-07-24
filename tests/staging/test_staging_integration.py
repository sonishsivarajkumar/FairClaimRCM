"""
Staging environment integration tests
"""

import pytest
import requests
import os
from typing import Dict, Any


class TestStagingAPI:
    """Integration tests for staging environment."""
    
    @pytest.fixture
    def staging_url(self):
        """Get staging URL from environment."""
        return os.getenv("STAGING_URL", "https://fairclaimrcm-staging.example.com")
    
    @pytest.fixture
    def api_key(self):
        """Get API key for staging."""
        return os.getenv("API_KEY")
    
    @pytest.fixture
    def headers(self, api_key):
        """Headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
    
    def test_health_check(self, staging_url):
        """Test health check endpoint."""
        response = requests.get(f"{staging_url}/health", timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_api_health_check(self, staging_url, headers):
        """Test API-specific health check."""
        response = requests.get(
            f"{staging_url}/api/v1/health", 
            headers=headers, 
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_icd10_validation(self, staging_url, headers):
        """Test ICD-10 code validation in staging."""
        test_codes = [
            ("E11.9", True),   # Valid diabetes code
            ("I21.9", True),   # Valid MI code
            ("INVALID", False) # Invalid code
        ]
        
        for code, should_be_valid in test_codes:
            response = requests.get(
                f"{staging_url}/api/v1/terminology/icd10/validate/{code}",
                headers=headers,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] == should_be_valid
            assert data["code"] == code
    
    def test_cpt_validation(self, staging_url, headers):
        """Test CPT code validation in staging."""
        test_codes = [
            ("99213", True),   # Valid office visit
            ("93458", True),   # Valid cardiac cath
            ("00000", False)   # Invalid code
        ]
        
        for code, should_be_valid in test_codes:
            response = requests.get(
                f"{staging_url}/api/v1/terminology/cpt/validate/{code}",
                headers=headers,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] == should_be_valid
    
    def test_code_recommendations(self, staging_url, headers):
        """Test code recommendation generation in staging."""
        request_data = {
            "claim_id": "STAGING_TEST_001",
            "clinical_text": "Patient with type 2 diabetes mellitus and hypertension requiring office visit",
            "include_explanations": True
        }
        
        response = requests.post(
            f"{staging_url}/api/v1/coding/recommendations",
            json=request_data,
            headers=headers,
            timeout=60  # Longer timeout for ML processing
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        assert "summary" in data
        assert "audit_id" in data
        assert isinstance(data["recommendations"], list)
        assert data["summary"]["total_recommendations"] >= 0
    
    def test_batch_recommendations(self, staging_url, headers):
        """Test batch recommendation processing in staging."""
        batch_requests = [
            {
                "claim_id": "STAGING_BATCH_001",
                "clinical_text": "Patient with diabetes mellitus"
            },
            {
                "claim_id": "STAGING_BATCH_002",
                "clinical_text": "Acute myocardial infarction treatment"
            }
        ]
        
        request_data = {
            "batch_requests": batch_requests,
            "include_explanations": False,
            "enable_parallel_processing": True
        }
        
        response = requests.post(
            f"{staging_url}/api/v1/coding/recommendations/batch",
            json=request_data,
            headers=headers,
            timeout=120  # Even longer timeout for batch processing
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "batch_id" in data
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 2
        assert data["summary"]["successful_requests"] >= 0
    
    def test_search_functionality(self, staging_url, headers):
        """Test search functionality in staging."""
        search_terms = ["diabetes", "cardiac", "surgery"]
        
        for term in search_terms:
            response = requests.get(
                f"{staging_url}/api/v1/terminology/icd10/search",
                params={"query": term, "limit": 10},
                headers=headers,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "codes" in data
            assert isinstance(data["codes"], list)
    
    def test_error_handling(self, staging_url, headers):
        """Test error handling in staging."""
        # Test malformed request
        response = requests.post(
            f"{staging_url}/api/v1/coding/recommendations",
            json={"invalid": "data"},
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self, staging_url, headers):
        """Test rate limiting (if implemented)."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = requests.get(
                f"{staging_url}/health",
                headers=headers,
                timeout=10
            )
            responses.append(response.status_code)
        
        # Most should succeed, rate limiting would return 429
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 5  # At least half should succeed


class TestStagingPerformance:
    """Performance tests for staging environment."""
    
    @pytest.fixture
    def staging_url(self):
        """Get staging URL from environment."""
        return os.getenv("STAGING_URL", "https://fairclaimrcm-staging.example.com")
    
    @pytest.fixture
    def headers(self):
        """Headers for API requests."""
        api_key = os.getenv("API_KEY")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers
    
    def test_response_times(self, staging_url, headers):
        """Test API response times."""
        import time
        
        # Test health check response time
        start_time = time.time()
        response = requests.get(f"{staging_url}/health", timeout=10)
        health_time = time.time() - start_time
        
        assert response.status_code == 200
        assert health_time < 2.0  # Should respond within 2 seconds
        
        # Test validation response time
        start_time = time.time()
        response = requests.get(
            f"{staging_url}/api/v1/terminology/icd10/validate/E11.9",
            headers=headers,
            timeout=10
        )
        validation_time = time.time() - start_time
        
        assert response.status_code == 200
        assert validation_time < 3.0  # Should validate within 3 seconds
    
    def test_concurrent_requests(self, staging_url, headers):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import time
        
        def make_request():
            response = requests.get(
                f"{staging_url}/api/v1/terminology/icd10/validate/E11.9",
                headers=headers,
                timeout=15
            )
            return response.status_code
        
        # Make 5 concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        # Should complete within reasonable time
        assert total_time < 10.0
