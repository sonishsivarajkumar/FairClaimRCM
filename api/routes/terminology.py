"""
Terminology API routes for FairClaimRCM

Handles medical terminology lookup and search operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from api.models.database import get_db
from api.models.schemas import TerminologyCode, SearchRequest, SearchResponse
from core.terminology.icd10_service import ICD10Service
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService

router = APIRouter()

@router.get("/icd10/search")
async def search_icd10_codes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search ICD-10 diagnosis codes by code or description.
    """
    icd10_service = ICD10Service()
    results = icd10_service.search_codes(q, limit)
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@router.get("/icd10/{code}")
async def get_icd10_code(code: str):
    """
    Get detailed information about a specific ICD-10 code.
    """
    icd10_service = ICD10Service()
    validation_result = icd10_service.validate_code(code)
    
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICD-10 code {code} not found"
        )
    
    # Add hierarchy information
    hierarchy = icd10_service.get_code_hierarchy(code)
    validation_result["hierarchy"] = hierarchy
    
    return validation_result

@router.get("/cpt/search")
async def search_cpt_codes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Search CPT procedure codes by code or description.
    """
    cpt_service = CPTService()
    
    if category:
        # Filter by category first
        category_results = cpt_service.get_codes_by_category(category)
        results = [r for r in category_results if q.lower() in r["code"].lower() or q.lower() in r["description"].lower()][:limit]
    else:
        results = cpt_service.search_codes(q, limit)
    
    return {
        "query": q,
        "category": category,
        "results": results,
        "total": len(results)
    }

@router.get("/cpt/{code}")
async def get_cpt_code(code: str):
    """
    Get detailed information about a specific CPT code.
    """
    cpt_service = CPTService()
    validation_result = cpt_service.validate_code(code)
    
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CPT code {code} not found"
        )
    
    return validation_result

@router.get("/cpt/categories")
async def get_cpt_categories():
    """
    Get list of available CPT categories.
    """
    cpt_service = CPTService()
    
    # Extract unique categories from codes
    categories = set()
    for code_data in cpt_service.codes_data.values():
        categories.add(code_data.get("category", "Unknown"))
    
    return {
        "categories": sorted(list(categories))
    }

@router.get("/drg/search")
async def search_drg_codes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search DRG codes by code or description.
    """
    drg_service = DRGService()
    results = drg_service.search_drgs(q, limit)
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@router.get("/drg/{code}")
async def get_drg_code(code: str):
    """
    Get detailed information about a specific DRG code.
    """
    drg_service = DRGService()
    validation_result = drg_service.validate_drg(code)
    
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DRG code {code} not found"
        )
    
    return validation_result

@router.get("/drg/{code}/reimbursement")
async def calculate_drg_reimbursement(
    code: str,
    base_rate: float = Query(5000.0, description="Hospital base rate"),
    wage_index: float = Query(1.0, description="Geographic wage index")
):
    """
    Calculate reimbursement estimate for a DRG code.
    """
    drg_service = DRGService()
    reimbursement_calc = drg_service.calculate_reimbursement(code, base_rate, wage_index)
    
    if "error" in reimbursement_calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=reimbursement_calc["error"]
        )
    
    return reimbursement_calc

@router.post("/lookup/batch")
async def batch_code_lookup(
    codes: dict  # {"icd10": ["I21.9"], "cpt": ["99213"], "drg": ["280"]}
):
    """
    Look up multiple codes across different terminology systems.
    """
    icd10_service = ICD10Service()
    cpt_service = CPTService()
    drg_service = DRGService()
    
    results = {
        "icd10": [],
        "cpt": [],
        "drg": []
    }
    
    # Look up ICD-10 codes
    for code in codes.get("icd10", []):
        result = icd10_service.validate_code(code)
        if result["valid"]:
            result["hierarchy"] = icd10_service.get_code_hierarchy(code)
        results["icd10"].append(result)
    
    # Look up CPT codes
    for code in codes.get("cpt", []):
        result = cpt_service.validate_code(code)
        results["cpt"].append(result)
    
    # Look up DRG codes
    for code in codes.get("drg", []):
        result = drg_service.validate_drg(code)
        results["drg"].append(result)
    
    return results

@router.get("/stats")
async def get_terminology_stats():
    """
    Get statistics about the terminology databases.
    """
    icd10_service = ICD10Service()
    cpt_service = CPTService()
    drg_service = DRGService()
    
    # Count codes in each system
    icd10_count = len(icd10_service.codes_data)
    cpt_count = len(cpt_service.codes_data)
    drg_count = len(drg_service.drg_data)
    
    # Get categories
    icd10_categories = set()
    for code_data in icd10_service.codes_data.values():
        icd10_categories.add(code_data.get("category", "Unknown"))
    
    cpt_categories = set()
    for code_data in cpt_service.codes_data.values():
        cpt_categories.add(code_data.get("category", "Unknown"))
    
    drg_mdcs = set()
    for drg_data in drg_service.drg_data.values():
        drg_mdcs.add(drg_data.get("mdc_description", "Unknown"))
    
    return {
        "icd10": {
            "total_codes": icd10_count,
            "categories": sorted(list(icd10_categories))
        },
        "cpt": {
            "total_codes": cpt_count,
            "categories": sorted(list(cpt_categories))
        },
        "drg": {
            "total_drgs": drg_count,
            "mdcs": sorted(list(drg_mdcs))
        },
        "total_codes": icd10_count + cpt_count + drg_count
    }

@router.get("/crosswalk/icd10-to-drg/{icd10_code}")
async def crosswalk_icd10_to_drg(icd10_code: str):
    """
    Find potential DRG codes for a given ICD-10 diagnosis code.
    """
    drg_service = DRGService()
    
    # Find DRG for single diagnosis
    drg_result = await drg_service.find_drg_by_diagnosis(icd10_code)
    
    if not drg_result:
        return {
            "icd10_code": icd10_code,
            "potential_drgs": [],
            "message": "No DRG mapping found for this ICD-10 code"
        }
    
    return {
        "icd10_code": icd10_code,
        "primary_drg": drg_result,
        "potential_drgs": [drg_result]
    }
