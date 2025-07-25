"""
Minimal FairClaimRCM FastAPI Application for testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="FairClaimRCM API",
    description="Transparent healthcare revenue cycle management API",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to FairClaimRCM API",
        "version": "0.3.0",
        "docs": "/docs",
        "description": "Transparent healthcare revenue cycle management"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "fairclaimrcm-api",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/claims/")
async def get_claims():
    # Mock data for frontend
    return {
        "data": [
            {
                "id": 1,
                "claim_id": "CLM-001",
                "patient_name": "John Doe",
                "created_at": "2025-01-15T10:00:00",
                "status": "pending",
                "total_amount": 1500.00
            },
            {
                "id": 2,
                "claim_id": "CLM-002", 
                "patient_name": "Jane Smith",
                "created_at": "2025-01-14T14:30:00",
                "status": "approved",
                "total_amount": 850.00
            },
            {
                "id": 3,
                "claim_id": "CLM-003",
                "patient_name": "Bob Johnson", 
                "created_at": "2025-01-13T09:15:00",
                "status": "denied",
                "total_amount": 2200.00
            }
        ]
    }
