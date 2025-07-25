"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class CodeType(str, Enum):
    ICD10 = "ICD10"
    CPT = "CPT"
    DRG = "DRG"

class ClaimStatus(str, Enum):
    PENDING = "pending"
    CODED = "coded"
    SUBMITTED = "submitted"
    PAID = "paid"
    DENIED = "denied"

class RecommendationSource(str, Enum):
    RULE_BASED = "rule_based"
    ML_MODEL = "ml_model"
    HYBRID = "hybrid"

# Base schemas
class ClaimBase(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier")
    patient_id: str = Field(..., description="Patient identifier")
    patient_name: Optional[str] = None
    service_date: Optional[date] = None
    total_amount: Optional[float] = None

class ClaimCreate(ClaimBase):
    pass

class ClaimUpdate(BaseModel):
    primary_diagnosis_code: Optional[str] = None
    secondary_diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    drg_code: Optional[str] = None
    status: Optional[ClaimStatus] = None

class Claim(ClaimBase):
    id: int
    primary_diagnosis_code: Optional[str] = None
    secondary_diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    drg_code: Optional[str] = None
    estimated_reimbursement: Optional[float] = None
    actual_reimbursement: Optional[float] = None
    status: ClaimStatus = ClaimStatus.PENDING
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Coding schemas
class CodingRequest(BaseModel):
    claim_id: str
    diagnosis_description: str
    procedure_descriptions: Optional[List[str]] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None

class CodeRecommendation(BaseModel):
    code: str
    description: str
    confidence: float
    source: RecommendationSource

class CodingResponse(BaseModel):
    claim_id: str
    icd10_recommendations: List[CodeRecommendation]
    cpt_recommendations: List[CodeRecommendation]
    drg_recommendation: Optional[CodeRecommendation] = None
    estimated_reimbursement: Optional[float] = None

# Audit schemas
class AuditLog(BaseModel):
    id: int
    claim_id: str
    action: str
    user_id: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Search schemas
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int

# Health check
class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.now)
