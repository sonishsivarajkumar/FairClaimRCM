"""
Performance tests using Locust for load testing
"""

from locust import HttpUser, task, between
import json
import random


class FairClaimRCMUser(HttpUser):
    """Simulated user for load testing FairClaimRCM API."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts."""
        # Health check on start
        self.client.get("/health")
    
    @task(3)
    def test_health_endpoint(self):
        """Test health check endpoint (frequent)."""
        self.client.get("/health")
    
    @task(2)
    def test_icd10_validation(self):
        """Test ICD-10 code validation."""
        codes = ["E11.9", "I21.9", "K35.9", "M25.512", "Z51.11"]
        code = random.choice(codes)
        
        with self.client.get(
            f"/api/v1/terminology/icd10/validate/{code}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Validation failed: {response.status_code}")
    
    @task(2)
    def test_cpt_validation(self):
        """Test CPT code validation."""
        codes = ["99213", "93458", "44970", "27447", "76700"]
        code = random.choice(codes)
        
        self.client.get(f"/api/v1/terminology/cpt/validate/{code}")
    
    @task(1)
    def test_code_search(self):
        """Test code search functionality."""
        search_terms = ["diabetes", "hypertension", "surgery", "cardiac", "fracture"]
        term = random.choice(search_terms)
        
        self.client.get(f"/api/v1/terminology/icd10/search?query={term}&limit=10")
    
    @task(1)
    def test_generate_recommendations(self):
        """Test code recommendation generation (most expensive operation)."""
        clinical_texts = [
            "Patient with type 2 diabetes mellitus and hypertension",
            "Acute myocardial infarction with chest pain",
            "Laparoscopic appendectomy for acute appendicitis",
            "Hip fracture requiring surgical repair",
            "Pneumonia with respiratory failure"
        ]
        
        request_data = {
            "claim_id": f"LOAD_TEST_{random.randint(1000, 9999)}",
            "clinical_text": random.choice(clinical_texts),
            "include_explanations": False  # Faster without explanations
        }
        
        with self.client.post(
            "/api/v1/coding/recommendations",
            json=request_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "recommendations" in data:
                    response.success()
                else:
                    response.failure("No recommendations in response")
            else:
                response.failure(f"Request failed: {response.status_code}")


class AdminUser(HttpUser):
    """Simulated admin user for testing administrative endpoints."""
    
    wait_time = between(5, 10)  # Admins make fewer requests
    
    @task(1)
    def test_audit_logs(self):
        """Test audit log retrieval."""
        self.client.get("/api/v1/audit/logs?limit=50")
    
    @task(1)
    def test_confidence_analytics(self):
        """Test confidence analytics endpoint."""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        self.client.get("/api/v1/coding/analytics/confidence", params=params)


class BatchProcessingUser(HttpUser):
    """Simulated user for batch processing operations."""
    
    wait_time = between(10, 30)  # Batch operations are less frequent
    
    @task(1)
    def test_batch_recommendations(self):
        """Test batch recommendation processing."""
        batch_requests = [
            {
                "claim_id": f"BATCH_{random.randint(1000, 9999)}_{i}",
                "clinical_text": f"Patient {i} with medical condition requiring treatment"
            }
            for i in range(5)  # Small batch for load testing
        ]
        
        request_data = {
            "batch_requests": batch_requests,
            "include_explanations": False,
            "enable_parallel_processing": True
        }
        
        with self.client.post(
            "/api/v1/coding/recommendations/batch",
            json=request_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data.get("results", [])) == 5:
                    response.success()
                else:
                    response.failure("Incomplete batch results")
            else:
                response.failure(f"Batch request failed: {response.status_code}")


# Custom load test scenarios
class QuickLoadTest(HttpUser):
    """Quick load test for basic functionality."""
    
    weight = 3  # Most common user type
    wait_time = between(1, 2)
    
    tasks = [
        FairClaimRCMUser.test_health_endpoint,
        FairClaimRCMUser.test_icd10_validation,
        FairClaimRCMUser.test_cpt_validation
    ]


class HeavyLoadTest(HttpUser):
    """Heavy load test including recommendation generation."""
    
    weight = 1  # Less common but resource-intensive
    wait_time = between(3, 5)
    
    tasks = [
        FairClaimRCMUser.test_generate_recommendations,
        BatchProcessingUser.test_batch_recommendations
    ]
