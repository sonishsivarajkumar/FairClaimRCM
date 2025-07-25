"""
Pytest configuration for FairClaimRCM test suite
"""

import pytest
import asyncio
import os
import sys
from typing import Generator, AsyncGenerator

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_fairclaimrcm.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    """Set up test database."""
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    # Import here to ensure test DB URL is set
    from api.models.database import engine, Base
    from sqlalchemy import create_engine
    
    # Create test engine
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_fairclaimrcm.db"):
        os.remove("./test_fairclaimrcm.db")

@pytest.fixture
def db_session(test_db):
    """Create a database session for testing."""
    from sqlalchemy.orm import sessionmaker
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
async def test_client():
    """Create test client for API testing."""
    from fastapi.testclient import TestClient
    from api.main import app
    
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_clinical_text():
    """Sample clinical text for testing."""
    return """
    Patient: John Doe, 65-year-old male
    Chief Complaint: Chest pain and shortness of breath
    
    History of Present Illness:
    Patient presents with acute onset chest pain that began 2 hours ago.
    Pain is described as crushing, substernal, radiating to left arm.
    Associated with diaphoresis and nausea.
    
    Past Medical History:
    - Hypertension
    - Type 2 Diabetes Mellitus
    - Hyperlipidemia
    
    Assessment and Plan:
    Acute myocardial infarction suspected.
    Patient underwent emergency cardiac catheterization.
    Percutaneous coronary intervention performed with stent placement.
    
    Procedures:
    - Cardiac catheterization
    - Percutaneous coronary intervention with drug-eluting stent
    
    Discharge Diagnosis:
    - Acute ST-elevation myocardial infarction
    - Coronary artery disease
    """

@pytest.fixture
def sample_batch_requests():
    """Sample batch requests for testing."""
    return [
        {
            "claim_id": "CLAIM_001",
            "clinical_text": "Patient with acute appendicitis underwent laparoscopic appendectomy."
        },
        {
            "claim_id": "CLAIM_002", 
            "clinical_text": "Type 2 diabetes mellitus with diabetic nephropathy. Patient on insulin therapy."
        },
        {
            "claim_id": "CLAIM_003",
            "clinical_text": "Hypertensive crisis with acute kidney injury. Emergency management required."
        }
    ]

# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "ml: mark test as a machine learning test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_data: mark test as requiring external data"
    )
