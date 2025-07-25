"""
Reimbursement Routes for FairClaimRCM

Handles comprehensive reimbursement calculations, fee schedules, 
and payment simulation.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date

from api.models.database import get_db
from api.services.reimbursement_service import ReimbursementEngine
from api.models.schemas import ClaimReimbursementRequest, ReimbursementResponse, FeeScheduleInfo

router = APIRouter()

@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_reimbursement(
    request: ClaimReimbursementRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate comprehensive reimbursement for a claim.
    
    - **claim_id**: Unique claim identifier
    - **cpt_codes**: List of CPT procedure codes
    - **icd10_codes**: List of ICD-10 diagnosis codes
    - **payer_type**: Type of payer (medicare, medicaid, commercial)
    - **payer_name**: Specific payer name (optional)
    - **state**: State for Medicaid calculations
    - **service_date**: Date of service
    - **modifiers**: CPT modifiers (optional)
    - **units**: Units for each CPT code (optional)
    """
    try:
        reimbursement_engine = ReimbursementEngine(db)
        
        calculation = await reimbursement_engine.calculate_claim_reimbursement(
            claim_id=request.claim_id,
            cpt_codes=request.cpt_codes,
            icd10_codes=request.icd10_codes,
            drg_code=request.drg_code,
            payer_type=request.payer_type,
            payer_name=request.payer_name,
            state=request.state,
            service_date=request.service_date,
            modifiers=request.modifiers,
            units=request.units
        )
        
        return calculation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate reimbursement: {str(e)}")

@router.get("/fee-schedule/{cpt_code}")
async def get_fee_schedule_info(
    cpt_code: str,
    payer_type: str = "medicare",
    db: Session = Depends(get_db)
):
    """
    Get detailed fee schedule information for a specific CPT code.
    
    - **cpt_code**: CPT procedure code
    - **payer_type**: Type of payer (medicare, medicaid, commercial)
    """
    try:
        reimbursement_engine = ReimbursementEngine(db)
        fee_info = await reimbursement_engine.get_fee_schedule_info(cpt_code, payer_type)
        
        if "error" in fee_info:
            raise HTTPException(status_code=404, detail=fee_info["error"])
        
        return fee_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get fee schedule info: {str(e)}")

@router.post("/simulate")
async def simulate_payment_scenarios(
    cpt_codes: List[str],
    icd10_codes: List[str],
    scenarios: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Simulate reimbursement across multiple payer scenarios.
    
    - **cpt_codes**: List of CPT procedure codes
    - **icd10_codes**: List of ICD-10 diagnosis codes
    - **scenarios**: List of payer scenarios to simulate
    
    Example scenarios:
    ```json
    [
        {
            "name": "Medicare",
            "payer_type": "medicare"
        },
        {
            "name": "Aetna Commercial",
            "payer_type": "commercial",
            "payer_name": "aetna"
        },
        {
            "name": "California Medicaid",
            "payer_type": "medicaid",
            "state": "CA"
        }
    ]
    ```
    """
    try:
        if not cpt_codes:
            raise HTTPException(status_code=400, detail="At least one CPT code is required")
        
        if not scenarios:
            raise HTTPException(status_code=400, detail="At least one scenario is required")
        
        reimbursement_engine = ReimbursementEngine(db)
        simulation_results = await reimbursement_engine.simulate_payment_scenarios(
            cpt_codes=cpt_codes,
            icd10_codes=icd10_codes,
            scenarios=scenarios
        )
        
        return simulation_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate payment scenarios: {str(e)}")

@router.get("/payers")
async def list_supported_payers():
    """
    List supported payers and their configuration.
    """
    return {
        "medicare": {
            "name": "Medicare",
            "type": "government",
            "supported_features": ["fee_schedule", "drg", "modifiers"],
            "coverage_areas": "nationwide"
        },
        "medicaid": {
            "name": "Medicaid",
            "type": "government",
            "supported_features": ["fee_schedule", "state_variations"],
            "coverage_areas": "state_specific",
            "supported_states": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA"]
        },
        "commercial": {
            "name": "Commercial Insurance",
            "type": "private",
            "supported_features": ["fee_schedule", "multipliers", "prior_auth"],
            "supported_payers": [
                {"name": "Aetna", "multiplier": 1.15},
                {"name": "Anthem", "multiplier": 1.20},
                {"name": "Cigna", "multiplier": 1.18},
                {"name": "United Healthcare", "multiplier": 1.22},
                {"name": "Humana", "multiplier": 1.12}
            ]
        }
    }

@router.get("/rates/comparison")
async def compare_reimbursement_rates(
    cpt_code: str,
    state: str = "default",
    db: Session = Depends(get_db)
):
    """
    Compare reimbursement rates across different payer types for a specific CPT code.
    
    - **cpt_code**: CPT procedure code to compare
    - **state**: State for Medicaid rate comparison
    """
    try:
        reimbursement_engine = ReimbursementEngine(db)
        
        # Get Medicare rate as baseline
        medicare_info = await reimbursement_engine.get_fee_schedule_info(cpt_code, "medicare")
        
        if "error" in medicare_info:
            raise HTTPException(status_code=404, detail=f"CPT code {cpt_code} not found")
        
        medicare_rate = medicare_info["payment_amount"]
        
        # Calculate rates for different payers
        comparison = {
            "cpt_code": cpt_code,
            "baseline_medicare_rate": medicare_rate,
            "rates": {
                "medicare": {
                    "amount": medicare_rate,
                    "percentage_of_medicare": 100
                },
                "medicaid": {
                    "amount": round(medicare_rate * reimbursement_engine.medicaid_rates.get(state, 0.80), 2),
                    "percentage_of_medicare": round(reimbursement_engine.medicaid_rates.get(state, 0.80) * 100, 1)
                },
                "commercial_avg": {
                    "amount": round(medicare_rate * 1.20, 2),  # Average commercial multiplier
                    "percentage_of_medicare": 120
                }
            },
            "commercial_payers": {}
        }
        
        # Add specific commercial payer rates
        for payer, multiplier in reimbursement_engine.commercial_multipliers.items():
            if payer != "default":
                comparison["commercial_payers"][payer] = {
                    "amount": round(medicare_rate * multiplier, 2),
                    "percentage_of_medicare": round(multiplier * 100, 1)
                }
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare rates: {str(e)}")

@router.post("/validate")
async def validate_claim_reimbursement(
    claim_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Validate a claim for reimbursement eligibility and identify potential issues.
    
    - **claim_data**: Complete claim information including codes, payer, etc.
    """
    try:
        reimbursement_engine = ReimbursementEngine(db)
        
        # Extract required fields
        cpt_codes = claim_data.get("cpt_codes", [])
        icd10_codes = claim_data.get("icd10_codes", [])
        payer_type = claim_data.get("payer_type", "medicare")
        payer_name = claim_data.get("payer_name")
        
        if not cpt_codes and not claim_data.get("drg_code"):
            raise HTTPException(status_code=400, detail="Either CPT codes or DRG code is required")
        
        # Validate coverage
        validation_result = await reimbursement_engine._validate_coverage(
            cpt_codes, icd10_codes, payer_type, payer_name
        )
        
        # Check for common issues
        issues = []
        warnings = []
        
        # Check for missing diagnosis codes with E&M services
        em_codes = [code for code in cpt_codes if code.startswith("99")]
        if em_codes and not icd10_codes:
            issues.append({
                "type": "missing_diagnosis",
                "severity": "high",
                "message": "Evaluation & Management services require supporting diagnosis codes",
                "affected_codes": em_codes
            })
        
        # Check for outdated codes (simplified check)
        outdated_codes = ["99201"]  # Example outdated code
        for code in cpt_codes:
            if code in outdated_codes:
                issues.append({
                    "type": "outdated_code",
                    "severity": "high",
                    "message": f"CPT code {code} is no longer valid",
                    "affected_codes": [code]
                })
        
        # Check for high-cost procedures
        high_cost_codes = ["00100", "00200"]  # Example high-cost codes
        for code in cpt_codes:
            if code in high_cost_codes:
                warnings.append({
                    "type": "high_cost_procedure",
                    "severity": "medium",
                    "message": f"CPT code {code} is a high-cost procedure that may require additional documentation",
                    "affected_codes": [code]
                })
        
        return {
            "validation_result": validation_result,
            "reimbursement_eligibility": "eligible" if not issues else "issues_found",
            "issues": issues,
            "warnings": warnings,
            "recommendations": [
                "Ensure all diagnosis codes support the procedures performed",
                "Verify that all required documentation is complete",
                "Check payer-specific requirements for high-cost procedures"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate claim: {str(e)}")
