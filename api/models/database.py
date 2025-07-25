"""
Database models and connection setup for FairClaimRCM
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import settings

# Database engine
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, unique=True, index=True)
    patient_id = Column(String, index=True)
    encounter_id = Column(String, index=True)
    
    # Clinical data
    chief_complaint = Column(Text)
    history_present_illness = Column(Text)
    discharge_summary = Column(Text)
    
    # Coding results
    primary_diagnosis_code = Column(String)
    secondary_diagnosis_codes = Column(JSON)  # List of codes
    procedure_codes = Column(JSON)  # List of CPT codes
    drg_code = Column(String)
    
    # Financial
    estimated_reimbursement = Column(Float)
    actual_reimbursement = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="pending")  # pending, coded, submitted, paid

class CodeRecommendation(Base):
    __tablename__ = "code_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    
    # Recommendation details
    code = Column(String, index=True)
    code_type = Column(String)  # ICD10, CPT, DRG
    confidence_score = Column(Float)
    reasoning = Column(Text)
    
    # Source
    recommendation_source = Column(String)  # rule_based, ml_model, hybrid
    model_version = Column(String)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String)
    approved = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, index=True)
    
    # Audit details
    action = Column(String)  # code_recommended, code_approved, claim_submitted
    details = Column(JSON)
    user_id = Column(String)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

class TerminologyCode(Base):
    __tablename__ = "terminology_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    code_system = Column(String, index=True)  # ICD10, CPT, DRG
    
    # Code details
    description = Column(Text)
    category = Column(String)
    billable = Column(Boolean, default=True)
    
    # Metadata
    version = Column(String)
    effective_date = Column(DateTime)
    
    # Additional data (weights, modifiers, etc.)
    additional_data = Column(JSON)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
