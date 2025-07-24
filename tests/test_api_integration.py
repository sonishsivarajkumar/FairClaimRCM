"""
Integration tests for FairClaimRCM API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from api.main import app
from api.models.database import Base, get_db


@pytest.mark.integration
class TestCodingAPI:
    """Integration tests for coding API endpoints."""
    
    @pytest.fixture(scope="class")
    def test_db_engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///./test_api.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        yield engine
        Base.metadata.drop_all(bind=engine)
    
    @pytest.fixture
    def test_db_session(self, test_db_engine):
        """Create test database session."""
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture
    def client(self, test_db_session):
        """Create test client with dependency override."""
        def override_get_db():
            try:
                yield test_db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_generate_recommendations(self, client, sample_clinical_text):
        """Test code recommendation generation endpoint."""
        request_data = {
            "claim_id": "TEST_CLAIM_001",
            "clinical_text": sample_clinical_text,
            "include_explanations": True
        }
        
        response = client.post("/api/v1/coding/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        assert "summary" in data
        assert "audit_id" in data
        assert isinstance(data["recommendations"], list)
        assert data["summary"]["total_recommendations"] >= 0
    
    def test_generate_recommendations_invalid_data(self, client):
        """Test recommendation generation with invalid data."""
        request_data = {
            "claim_id": "",  # Empty claim ID
            "clinical_text": "",  # Empty text
        }
        
        response = client.post("/api/v1/coding/analyze", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_batch_recommendations(self, client, sample_batch_requests):
        """Test batch recommendation generation."""
        # The API expects batch_requests as JSON body and other params as query params
        response = client.post(
            "/api/v1/coding/analyze/batch?include_explanations=true&enable_parallel_processing=false", 
            json=sample_batch_requests
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # The API returns batch_results which contains the nested results
        assert "status" in data
        assert data["status"] == "success"
        assert "batch_results" in data
        assert "results" in data["batch_results"]
        assert len(data["batch_results"]["results"]) == len(sample_batch_requests)
    
    def test_get_recommendations_by_claim(self, client):
        """Test retrieving recommendations by claim ID."""
        # First generate some recommendations
        request_data = {
            "claim_id": "TEST_CLAIM_002",
            "clinical_text": "Patient with diabetes mellitus type 2",
            "include_explanations": True
        }
        
        client.post("/api/v1/coding/analyze", json=request_data)
        
        # Now retrieve them
        response = client.get("/api/v1/coding/recommendations/TEST_CLAIM_002")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)  # API returns a list of recommendations
    
    def test_get_recommendations_by_claim_not_found(self, client):
        """Test retrieving recommendations for non-existent claim."""
        response = client.get("/api/v1/coding/recommendations/NONEXISTENT_CLAIM")
        
        assert response.status_code == 404  # Should return 404 for non-existent claim
    
    def test_validate_recommendations(self, client):
        """Test recommendation validation."""
        # First generate recommendations
        request_data = {
            "claim_id": "TEST_CLAIM_003",
            "clinical_text": "Patient with acute myocardial infarction",
            "include_explanations": True
        }
        
        client.post("/api/v1/coding/analyze", json=request_data)
        
        # Now validate
        response = client.post("/api/v1/coding/validate", json={"claim_id": "TEST_CLAIM_003"})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["claim_id"] == "TEST_CLAIM_003"
        assert "validation_passed" in data
        assert "issues" in data
        assert "warnings" in data
        assert "suggestions" in data


@pytest.mark.integration
class TestTerminologyAPI:
    """Integration tests for terminology API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as test_client:
            yield test_client
    
    def test_search_icd10_codes(self, client):
        """Test ICD-10 code search."""
        response = client.get("/api/v1/terminology/icd10/search?query=diabetes")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "codes" in data
        assert isinstance(data["codes"], list)
    
    def test_validate_icd10_code(self, client):
        """Test ICD-10 code validation."""
        response = client.get("/api/v1/terminology/icd10/validate/E11.9")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "code" in data
        assert data["code"] == "E11.9"
    
    def test_search_cpt_codes(self, client):
        """Test CPT code search."""
        response = client.get("/api/v1/terminology/cpt/search?query=office visit")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "codes" in data
        assert isinstance(data["codes"], list)
    
    def test_validate_cpt_code(self, client):
        """Test CPT code validation."""
        response = client.get("/api/v1/terminology/cpt/validate/99213")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "code" in data
        assert data["code"] == "99213"


@pytest.mark.integration
class TestAuditAPI:
    """Integration tests for audit API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as test_client:
            yield test_client
    
    def test_get_audit_logs(self, client):
        """Test retrieving audit logs."""
        response = client.get("/api/v1/audit/logs?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total_count" in data
        assert isinstance(data["logs"], list)
    
    def test_get_audit_logs_by_claim(self, client):
        """Test retrieving audit logs for specific claim."""
        response = client.get("/api/v1/audit/logs/TEST_CLAIM_001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert isinstance(data["logs"], list)


@pytest.mark.api
@pytest.mark.slow
class TestPerformanceAPI:
    """Performance tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as test_client:
            yield test_client
    
    def test_recommendations_response_time(self, client, sample_clinical_text):
        """Test that recommendation generation completes within acceptable time."""
        import time
        
        request_data = {
            "claim_id": "PERF_TEST_001",
            "clinical_text": sample_clinical_text,
            "include_explanations": True
        }
        
        start_time = time.time()
        response = client.post("/api/v1/coding/analyze", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
    
    def test_batch_recommendations_performance(self, client):
        """Test batch processing performance."""
        import time
        
        # Create larger batch for performance testing
        batch_requests = [
            {
                "claim_id": f"PERF_BATCH_{i}",
                "clinical_text": f"Patient {i} with condition requiring treatment"
            }
            for i in range(10)
        ]
        
        request_data = {
            "batch_requests": batch_requests,
            "include_explanations": False,  # Faster without explanations
            "enable_parallel_processing": True
        }
        
        start_time = time.time()
        response = client.post(
            "/api/v1/coding/analyze/batch?include_explanations=false&enable_parallel_processing=true",
            json=batch_requests
        )
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should process 10 requests faster than 10 individual requests
        assert (end_time - start_time) < 30.0
        
        data = response.json()
        assert "batch_results" in data
        assert len(data["batch_results"]["results"]) == 10
        assert data["batch_results"]["summary"]["successful_requests"] == 10
