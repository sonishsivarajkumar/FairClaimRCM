"""
Coding API routes for FairClaimRCM

Handles medical coding operations and recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from api.models.database import get_db
from api.models.schemas import (
    CodeRecommendation, CodingRequest, CodingResponse,
    ReimbursementRequest, ReimbursementEstimate
)
from api.services.coding_service import CodingService
from core.terminology.icd10_service import ICD10Service
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService

router = APIRouter()

@router.post("/analyze", response_model=CodingResponse)
async def analyze_clinical_text(
    coding_request: CodingRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze clinical text and generate coding recommendations.
    
    This endpoint provides the core coding functionality, analyzing
    clinical documentation and returning ICD-10, CPT, and DRG recommendations.
    """
    coding_service = CodingService(db)
    
    # Use a generated claim ID if not provided
    claim_id = coding_request.claim_id or f"temp-{hash(coding_request.clinical_text)}"
    
    response = await coding_service.generate_recommendations(
        claim_id=claim_id,
        clinical_text=coding_request.clinical_text,
        include_explanations=coding_request.include_explanations
    )
    
    return response

@router.post("/validate", response_model=dict)
async def validate_codes(
    codes: dict,  # {"icd10": ["I21.9"], "cpt": ["99213"], "drg": ["280"]}
    db: Session = Depends(get_db)
):
    """
    Validate a set of medical codes.
    
    Checks if the provided codes are valid and returns detailed information
    about each code including descriptions and categories.
    """
    icd10_service = ICD10Service()
    cpt_service = CPTService()
    drg_service = DRGService()
    
    validation_results = {
        "icd10": [],
        "cpt": [],
        "drg": [],
        "overall_valid": True
    }
    
    # Validate ICD-10 codes
    for code in codes.get("icd10", []):
        result = icd10_service.validate_code(code)
        validation_results["icd10"].append(result)
        if not result["valid"]:
            validation_results["overall_valid"] = False
    
    # Validate CPT codes
    for code in codes.get("cpt", []):
        result = cpt_service.validate_code(code)
        validation_results["cpt"].append(result)
        if not result["valid"]:
            validation_results["overall_valid"] = False
    
    # Validate DRG codes
    for code in codes.get("drg", []):
        result = drg_service.validate_drg(code)
        validation_results["drg"].append(result)
        if not result["valid"]:
            validation_results["overall_valid"] = False
    
    return validation_results

@router.post("/reimbursement/estimate", response_model=ReimbursementEstimate)
async def estimate_reimbursement(
    request: ReimbursementRequest,
    db: Session = Depends(get_db)
):
    """
    Estimate reimbursement for a set of diagnosis and procedure codes.
    
    Calculates expected reimbursement based on DRG assignment and
    current fee schedules.
    """
    drg_service = DRGService()
    
    if not request.diagnosis_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one diagnosis code is required"
        )
    
    primary_diagnosis = request.diagnosis_codes[0]
    secondary_diagnoses = request.diagnosis_codes[1:] if len(request.diagnosis_codes) > 1 else []
    
    # Find appropriate DRG
    drg_result = await drg_service.find_drg_by_diagnosis(
        primary_diagnosis, secondary_diagnoses
    )
    
    if not drg_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No DRG found for diagnosis codes: {request.diagnosis_codes}"
        )
    
    # Calculate reimbursement estimate
    reimbursement_calc = drg_service.calculate_reimbursement(
        drg_code=drg_result["code"],
        base_rate=5000.0,  # Default base rate
        wage_index=1.0     # Default wage index
    )
    
    # Apply complexity adjustments
    complexity_adjustment = 1.0
    if drg_result["complexity_level"] == "MCC":
        complexity_adjustment = 1.2
    elif drg_result["complexity_level"] == "CC":
        complexity_adjustment = 1.1
    
    final_payment = reimbursement_calc["estimated_payment"] * complexity_adjustment
    
    explanation = (
        f"DRG {drg_result['code']}: {drg_result['description']}. "
        f"Base payment: ${reimbursement_calc['estimated_payment']:.2f}. "
        f"Complexity adjustment ({drg_result['complexity_level']}): {complexity_adjustment:.1f}x. "
        f"Final estimated payment: ${final_payment:.2f}"
    )
    
    return ReimbursementEstimate(
        drg_code=drg_result["code"],
        base_rate=reimbursement_calc["base_rate"],
        complexity_adjustment=complexity_adjustment,
        estimated_payment=final_payment,
        confidence=drg_result["confidence"],
        explanation=explanation
    )

@router.get("/recommendations/{claim_id}", response_model=List[CodeRecommendation])
async def get_claim_recommendations(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve existing coding recommendations for a claim.
    """
    from api.models.database import CodeRecommendation as CodeRecommendationModel
    
    recommendations = db.query(CodeRecommendationModel).filter(
        CodeRecommendationModel.claim_id == claim_id
    ).all()
    
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No recommendations found for claim {claim_id}"
        )
    
    return recommendations

@router.put("/recommendations/{recommendation_id}/approve")
async def approve_recommendation(
    recommendation_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Approve a coding recommendation.
    
    Marks a recommendation as reviewed and approved by a user.
    """
    from api.models.database import CodeRecommendation as CodeRecommendationModel
    from api.services.audit_service import AuditService
    
    recommendation = db.query(CodeRecommendationModel).filter(
        CodeRecommendationModel.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found"
        )
    
    # Update recommendation
    recommendation.approved = True
    recommendation.reviewed_by = user_id
    db.commit()
    
    # Log approval
    audit_service = AuditService(db)
    await audit_service.log_action(
        claim_id=recommendation.claim_id,
        action="recommendation_approved",
        details={
            "recommendation_id": recommendation_id,
            "code": recommendation.code,
            "code_type": recommendation.code_type,
            "confidence_score": recommendation.confidence_score
        },
        user_id=user_id
    )
    
    return {"message": "Recommendation approved successfully"}

@router.get("/quality/metrics")
async def get_coding_quality_metrics(
    db: Session = Depends(get_db)
):
    """
    Get coding quality metrics and statistics.
    
    Provides insights into coding accuracy, consistency, and performance.
    """
    from api.models.database import CodeRecommendation as CodeRecommendationModel, Claim as ClaimModel
    from sqlalchemy import func
    
    # Total recommendations
    total_recommendations = db.query(CodeRecommendationModel).count()
    
    # Approved recommendations
    approved_recommendations = db.query(CodeRecommendationModel).filter(
        CodeRecommendationModel.approved == True
    ).count()
    
    # Average confidence score
    avg_confidence = db.query(func.avg(CodeRecommendationModel.confidence_score)).scalar() or 0
    
    # Recommendations by code type
    code_type_stats = db.query(
        CodeRecommendationModel.code_type,
        func.count(CodeRecommendationModel.id)
    ).group_by(CodeRecommendationModel.code_type).all()
    
    # Recommendations by source
    source_stats = db.query(
        CodeRecommendationModel.recommendation_source,
        func.count(CodeRecommendationModel.id)
    ).group_by(CodeRecommendationModel.recommendation_source).all()
    
    # Claims by status
    claims_by_status = db.query(
        ClaimModel.status,
        func.count(ClaimModel.id)
    ).group_by(ClaimModel.status).all()
    
    return {
        "total_recommendations": total_recommendations,
        "approved_recommendations": approved_recommendations,
        "approval_rate": approved_recommendations / total_recommendations if total_recommendations > 0 else 0,
        "average_confidence": round(avg_confidence, 3),
        "code_type_distribution": dict(code_type_stats),
        "source_distribution": dict(source_stats),
        "claims_by_status": dict(claims_by_status)
    }
