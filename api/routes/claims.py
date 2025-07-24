"""
Claims API routes for FairClaimRCM

Handles claim submission, retrieval, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from api.models.database import get_db, Claim as ClaimModel, AuditLog as AuditLogModel
from api.models.schemas import (
    Claim, ClaimCreate, ClaimUpdate, CodingRequest, CodingResponse,
    AuditLog, SearchRequest, SearchResponse
)
from api.services.coding_service import CodingService
from api.services.audit_service import AuditService

router = APIRouter()

@router.post("/", response_model=Claim, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim: ClaimCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new claim for processing.
    
    This endpoint accepts clinical data and creates a new claim record
    that can then be processed for coding recommendations.
    """
    # Check if claim ID already exists
    existing_claim = db.query(ClaimModel).filter(
        ClaimModel.claim_id == claim.claim_id
    ).first()
    
    if existing_claim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim with ID {claim.claim_id} already exists"
        )
    
    # Create new claim
    db_claim = ClaimModel(**claim.dict())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    
    # Log creation
    audit_service = AuditService(db)
    await audit_service.log_action(
        claim_id=claim.claim_id,
        action="claim_created",
        details={"claim_data": claim.dict()},
        user_id="system"
    )
    
    return db_claim

@router.get("/{claim_id}", response_model=Claim)
async def get_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific claim by ID.
    """
    claim = db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    return claim

@router.put("/{claim_id}", response_model=Claim)
async def update_claim(
    claim_id: str,
    claim_update: ClaimUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing claim with new coding information.
    """
    claim = db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    # Update fields
    update_data = claim_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(claim, field, value)
    
    db.commit()
    db.refresh(claim)
    
    # Log update
    audit_service = AuditService(db)
    await audit_service.log_action(
        claim_id=claim_id,
        action="claim_updated",
        details={"updated_fields": update_data},
        user_id="system"
    )
    
    return claim

@router.get("/", response_model=List[Claim])
async def list_claims(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    patient_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List claims with optional filtering.
    """
    query = db.query(ClaimModel)
    
    if status:
        query = query.filter(ClaimModel.status == status)
    
    if patient_id:
        query = query.filter(ClaimModel.patient_id == patient_id)
    
    claims = query.offset(skip).limit(limit).all()
    return claims

@router.post("/{claim_id}/code", response_model=CodingResponse)
async def code_claim(
    claim_id: str,
    coding_request: CodingRequest,
    db: Session = Depends(get_db)
):
    """
    Generate coding recommendations for a claim.
    
    Analyzes the clinical text and returns suggested ICD-10, CPT, and DRG codes
    with confidence scores and explanations.
    """
    # Verify claim exists
    claim = db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    # Get coding recommendations
    coding_service = CodingService(db)
    response = await coding_service.generate_recommendations(
        claim_id=claim_id,
        clinical_text=coding_request.clinical_text,
        include_explanations=coding_request.include_explanations
    )
    
    # Update claim status
    claim.status = "coded"
    db.commit()
    
    return response

@router.get("/{claim_id}/audit", response_model=List[AuditLog])
async def get_claim_audit_trail(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete audit trail for a claim.
    """
    # Verify claim exists
    claim = db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    # Get audit logs
    audit_logs = db.query(AuditLogModel).filter(
        AuditLogModel.claim_id == claim_id
    ).order_by(AuditLogModel.timestamp.desc()).all()
    
    return audit_logs

@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_claim(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a claim and all associated data.
    """
    claim = db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )
    
    # Log deletion before removing
    audit_service = AuditService(db)
    await audit_service.log_action(
        claim_id=claim_id,
        action="claim_deleted",
        details={"deleted_claim": claim.claim_id},
        user_id="system"
    )
    
    db.delete(claim)
    db.commit()

@router.post("/search", response_model=SearchResponse)
async def search_claims(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search claims using full-text search.
    """
    # Basic implementation - can be enhanced with Elasticsearch
    query = db.query(ClaimModel)
    
    # Simple text search in clinical fields
    search_term = f"%{search_request.query}%"
    query = query.filter(
        ClaimModel.chief_complaint.contains(search_term) |
        ClaimModel.history_present_illness.contains(search_term) |
        ClaimModel.discharge_summary.contains(search_term)
    )
    
    # Apply filters if provided
    if search_request.filters:
        for key, value in search_request.filters.items():
            if hasattr(ClaimModel, key):
                query = query.filter(getattr(ClaimModel, key) == value)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    results = query.offset(search_request.offset).limit(search_request.limit).all()
    
    return SearchResponse(
        results=[claim.__dict__ for claim in results],
        total=total,
        limit=search_request.limit,
        offset=search_request.offset
    )
