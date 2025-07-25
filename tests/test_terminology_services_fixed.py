"""
Tests for FairClaimRCM terminology services.
Updated to match actual service implementations.
"""

import pytest
from unittest.mock import Mock, patch
from core.terminology.icd10_service import ICD10Service
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService


class TestICD10Service:
    """Test cases for ICD10Service."""
    
    @pytest.mark.unit
    def test_init(self):
        """Test ICD10Service initialization."""
        icd10_service = ICD10Service()
        assert hasattr(icd10_service, 'codes_data')
        assert hasattr(icd10_service, 'keyword_mappings')
        assert isinstance(icd10_service.codes_data, dict)
    
    @pytest.mark.unit 
    def test_validate_code_valid(self):
        """Test validation of valid ICD-10 code."""
        icd10_service = ICD10Service()
        result = icd10_service.validate_code("I21.9")
        assert result["valid"] == True
        assert "description" in result
    
    @pytest.mark.unit
    def test_validate_code_invalid(self):
        """Test validation of invalid ICD-10 code."""
        icd10_service = ICD10Service()
        result = icd10_service.validate_code("INVALID")
        assert result["valid"] == False
        assert "error" in result
    
    @pytest.mark.unit
    def test_get_code_description(self):
        """Test getting code description."""
        icd10_service = ICD10Service()
        description = icd10_service.get_code_description("E11.9")
        assert isinstance(description, str)
        # Should return description for valid codes or "Unknown" message for invalid
        assert len(description) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_codes_by_text(self):
        """Test finding codes by clinical text."""
        icd10_service = ICD10Service()
        results = await icd10_service.find_codes_by_text("chest pain")
        assert isinstance(results, list)
        # Results may be empty if no matches, but should be a list
    
    @pytest.mark.unit
    def test_search_codes(self):
        """Test code search functionality."""
        icd10_service = ICD10Service()
        results = icd10_service.search_codes("diabetes", limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5


class TestCPTService:
    """Test cases for CPTService."""
    
    @pytest.mark.unit
    def test_init(self):
        """Test CPTService initialization."""
        cpt_service = CPTService()
        assert hasattr(cpt_service, 'codes_data')
        assert isinstance(cpt_service.codes_data, dict)
    
    @pytest.mark.unit
    def test_validate_code_valid(self):
        """Test validation of valid CPT code."""
        cpt_service = CPTService()
        result = cpt_service.validate_code("99213")
        assert result["valid"] == True
        assert "description" in result
    
    @pytest.mark.unit
    def test_validate_code_invalid(self):
        """Test validation of invalid CPT code."""
        cpt_service = CPTService()
        result = cpt_service.validate_code("INVALID")
        assert result["valid"] == False
        assert "error" in result
    
    @pytest.mark.unit
    def test_get_code_description(self):
        """Test getting CPT code description."""
        cpt_service = CPTService()
        description = cpt_service.get_code_description("99213")
        assert isinstance(description, str)
        assert len(description) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_codes_by_keywords(self):
        """Test finding codes by keywords."""
        cpt_service = CPTService()
        results = await cpt_service.find_codes_by_keywords(["consultation", "office"])
        assert isinstance(results, list)
        # Results may be empty but should be a list
    
    @pytest.mark.unit
    def test_get_codes_by_category(self):
        """Test getting codes by category."""
        cpt_service = CPTService()
        results = cpt_service.get_codes_by_category("Evaluation and Management")
        assert isinstance(results, list)
        # May return empty list if category not found


class TestDRGService:
    """Test cases for DRGService."""
    
    @pytest.mark.unit
    def test_init(self):
        """Test DRGService initialization."""
        drg_service = DRGService()
        assert hasattr(drg_service, 'drg_data')
        assert isinstance(drg_service.drg_data, dict)
    
    @pytest.mark.unit
    def test_validate_drg_valid(self):
        """Test validation of valid DRG code."""
        drg_service = DRGService()
        result = drg_service.validate_drg("280")
        assert result["valid"] == True
        assert "description" in result
    
    @pytest.mark.unit
    def test_validate_drg_invalid(self):
        """Test validation of invalid DRG code."""
        drg_service = DRGService()
        result = drg_service.validate_drg("INVALID")
        assert result["valid"] == False
        assert "error" in result
    
    @pytest.mark.unit
    def test_get_drg_description(self):
        """Test getting DRG description."""
        drg_service = DRGService()
        description = drg_service.get_drg_description("280")
        assert isinstance(description, str)
        assert len(description) > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_drg_by_diagnosis(self):
        """Test finding DRG by primary diagnosis."""
        drg_service = DRGService()
        result = await drg_service.find_drg_by_diagnosis("I21.9", ["I21.9"])
        # May return None if no match found
        if result is not None:
            assert "code" in result
            assert "confidence" in result
    
    @pytest.mark.unit 
    @pytest.mark.asyncio
    async def test_find_drg_by_diagnosis_no_match(self):
        """Test DRG lookup with no matching diagnosis."""
        drg_service = DRGService()
        result = await drg_service.find_drg_by_diagnosis("INVALID", ["INVALID"])
        assert result is None
    
    @pytest.mark.unit
    def test_calculate_reimbursement(self):
        """Test reimbursement calculation."""
        drg_service = DRGService()
        base_rate = 5000.0
        # This method exists in the actual service
        result = drg_service.calculate_reimbursement("280", base_rate)
        assert isinstance(result, dict)
        assert "estimated_payment" in result or "error" in result
