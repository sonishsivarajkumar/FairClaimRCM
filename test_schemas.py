"""
Minimal test schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    PENDING = "pending"
    CODED = "coded"
    SUBMITTED = "submitted"
    PAID = "paid"
    DENIED = "denied"

class ClaimBase(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier")
    patient_id: str = Field(..., description="Patient identifier")

class Claim(ClaimBase):
    id: int
    status: ClaimStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
