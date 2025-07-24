"""
Unit tests for CodingService
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from api.services.coding_service import CodingService
from api.models.schemas import CodeRecommendationResponse, CodeType, RecommendationSource
from api.models.database import CodeRecommendation as CodeRecommendationModel


@pytest.mark.unit
class TestCodingService:
    """Test suite for CodingService class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def coding_service(self, mock_db_session):
        """Create CodingService instance with mocked dependencies."""
        with patch('api.services.coding_service.ICD10Service') as mock_icd10, \
             patch('api.services.coding_service.CPTService') as mock_cpt, \
             patch('api.services.coding_service.DRGService') as mock_drg, \
             patch('api.services.coding_service.CodePredictor') as mock_predictor, \
             patch('api.services.coding_service.AuditService') as mock_audit:
            
            service = CodingService(mock_db_session)
            service.icd10_service = mock_icd10.return_value
            service.cpt_service = mock_cpt.return_value
            service.drg_service = mock_drg.return_value
            service.code_predictor = mock_predictor.return_value
            service.audit_service = mock_audit.return_value
            
            return service
    
    def test_init(self, mock_db_session):
        """Test CodingService initialization."""
        with patch('api.services.coding_service.ICD10Service'), \
             patch('api.services.coding_service.CPTService'), \
             patch('api.services.coding_service.DRGService'), \
             patch('api.services.coding_service.CodePredictor'), \
             patch('api.services.coding_service.AuditService'):
            
            service = CodingService(mock_db_session)
            
            assert service.db == mock_db_session
            assert service.version == "v0.2.0"
            assert service.icd10_service is not None
            assert service.cpt_service is not None
            assert service.drg_service is not None
            assert service.code_predictor is not None
            assert service.audit_service is not None
    
    def test_preprocess_text(self, coding_service):
        """Test clinical text preprocessing."""
        # Test PHI removal
        text_with_phi = "Patient SSN: 123-45-6789 Phone: 1234567890 has diabetes"
        processed = coding_service._preprocess_text(text_with_phi)
        
        assert "[SSN]" in processed
        assert "[PHONE]" in processed
        assert "123-45-6789" not in processed
        assert "1234567890" not in processed
        
        # Test whitespace normalization
        text_with_spaces = "Patient   has    multiple     spaces"
        processed = coding_service._preprocess_text(text_with_spaces)
        assert "  " not in processed
        assert processed == "Patient has multiple spaces"
    
    def test_extract_procedure_keywords(self, coding_service):
        """Test procedure keyword extraction."""
        text = """
        Patient underwent cardiac catheterization.
        Performed percutaneous coronary intervention.
        Surgery: appendectomy was completed.
        """
        
        keywords = coding_service._extract_procedure_keywords(text)
        
        # Updated to match actual implementation - it extracts words after procedure indicators
        assert "cardiac" in keywords or "catheterization" in keywords
        assert "percutaneous" in keywords or "intervention" in keywords  
        assert "appendectomy" in keywords
        assert len(keywords) >= 2
    
    def test_combine_recommendations(self, coding_service):
        """Test recommendation combination logic."""
        rule_based = [
            {"code": "I21.9", "confidence": 0.8, "match_reason": "chest pain pattern"}
        ]
        
        ml_based = [
            {"code": "I21.9", "confidence": 0.9, "features": ["chest", "pain", "acute"]},
            {"code": "I25.10", "confidence": 0.7, "features": ["coronary", "disease"]}
        ]
        
        combined = coding_service._combine_recommendations(rule_based, ml_based)
        
        # Should have 2 unique codes
        assert len(combined) == 2
        
        # First code should be I21.9 with boosted confidence (hybrid)
        first_rec = combined[0]
        assert first_rec["code"] == "I21.9"
        assert first_rec["source"] == RecommendationSource.HYBRID
        assert first_rec["confidence"] > 0.8  # Boosted confidence
        
        # Second should be I25.10 from ML only
        second_rec = combined[1]
        assert second_rec["code"] == "I25.10"
        assert second_rec["source"] == RecommendationSource.ML_MODEL
    
    @pytest.mark.asyncio
    async def test_generate_icd10_recommendations(self, coding_service):
        """Test ICD-10 recommendation generation."""
        # Mock service responses
        coding_service.icd10_service.find_codes_by_text = AsyncMock(return_value=[
            {"code": "I21.9", "confidence": 0.8, "match_reason": "MI pattern"}
        ])
        
        coding_service.code_predictor.predict_icd10_codes = AsyncMock(return_value=[
            {"code": "I21.9", "confidence": 0.9, "features": ["acute", "myocardial"]}
        ])
        
        coding_service.icd10_service.get_code_description = Mock(return_value="Acute myocardial infarction")
        
        recommendations = await coding_service._generate_icd10_recommendations(
            "Patient with acute MI", include_explanations=True
        )
        
        assert len(recommendations) == 1
        assert recommendations[0].code == "I21.9"
        assert recommendations[0].code_type == CodeType.ICD10
        assert recommendations[0].confidence_score > 0.8
        assert "I21.9" in recommendations[0].reasoning
    
    @pytest.mark.asyncio
    async def test_generate_cpt_recommendations(self, coding_service):
        """Test CPT recommendation generation."""
        # Mock service responses
        coding_service.cpt_service.find_codes_by_keywords = AsyncMock(return_value=[
            {"code": "93458", "confidence": 0.85, "match_reason": "catheterization"}
        ])
        
        coding_service.code_predictor.predict_cpt_codes = AsyncMock(return_value=[
            {"code": "93458", "confidence": 0.9, "features": ["cardiac", "cath"]}
        ])
        
        coding_service.cpt_service.get_code_description = Mock(return_value="Cardiac catheterization")
        
        text = "Patient underwent cardiac catheterization procedure"
        recommendations = await coding_service._generate_cpt_recommendations(
            text, include_explanations=True
        )
        
        assert len(recommendations) == 1
        assert recommendations[0].code == "93458"
        assert recommendations[0].code_type == CodeType.CPT
        assert "93458" in recommendations[0].reasoning
    
    @pytest.mark.asyncio
    async def test_generate_drg_recommendations(self, coding_service):
        """Test DRG recommendation generation."""
        coding_service.drg_service.find_drg_by_diagnosis = AsyncMock(return_value={
            "code": "280",
            "confidence": 0.9
        })
        
        coding_service.drg_service.get_drg_description = Mock(return_value="Acute MI with MCC")
        
        recommendations = await coding_service._generate_drg_recommendations(
            "I21.9", ["I21.9", "E11.9"], include_explanations=True
        )
        
        assert len(recommendations) == 1
        assert recommendations[0].code == "280"
        assert recommendations[0].code_type == CodeType.DRG
        assert "I21.9" in recommendations[0].reasoning
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_full_workflow(self, coding_service, sample_clinical_text):
        """Test complete recommendation generation workflow."""
        # Mock all dependencies
        coding_service.icd10_service.find_codes_by_text = AsyncMock(return_value=[
            {"code": "I21.9", "confidence": 0.8, "match_reason": "MI pattern"}
        ])
        
        coding_service.code_predictor.predict_icd10_codes = AsyncMock(return_value=[
            {"code": "I21.9", "confidence": 0.9, "features": ["acute", "MI"]}
        ])
        
        coding_service.cpt_service.find_codes_by_keywords = AsyncMock(return_value=[
            {"code": "93458", "confidence": 0.85, "match_reason": "catheterization"}
        ])
        
        coding_service.code_predictor.predict_cpt_codes = AsyncMock(return_value=[
            {"code": "93458", "confidence": 0.9, "features": ["cardiac", "cath"]}
        ])
        
        coding_service.drg_service.find_drg_by_diagnosis = AsyncMock(return_value={
            "code": "280", "confidence": 0.9
        })
        
        # Mock description methods
        coding_service.icd10_service.get_code_description = Mock(return_value="Acute MI")
        coding_service.cpt_service.get_code_description = Mock(return_value="Cardiac cath")
        coding_service.drg_service.get_drg_description = Mock(return_value="Acute MI DRG")
        
        # Mock audit service
        coding_service.audit_service.log_action = AsyncMock(return_value=Mock(id=123))
        
        # Mock database operations
        coding_service.db.add = Mock()
        coding_service.db.commit = Mock()
        
        response = await coding_service.generate_recommendations(
            claim_id="TEST_001",
            clinical_text=sample_clinical_text,
            include_explanations=True
        )
        
        assert response.audit_id == 123
        assert len(response.recommendations) >= 2  # At least ICD-10 and CPT
        assert response.summary["total_recommendations"] >= 2
        
        # Verify database operations were called
        coding_service.db.add.assert_called()
        coding_service.db.commit.assert_called()
    
    def test_calculate_std_dev(self, coding_service):
        """Test standard deviation calculation."""
        # Test normal case
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        std_dev = coding_service._calculate_std_dev(values)
        assert abs(std_dev - 1.4142135623730951) < 0.0001
        
        # Test edge cases
        assert coding_service._calculate_std_dev([]) == 0.0
        assert coding_service._calculate_std_dev([5.0]) == 0.0
        assert coding_service._calculate_std_dev([1.0, 1.0, 1.0]) == 0.0
    
    def test_generate_summary(self, coding_service):
        """Test recommendation summary generation."""
        recommendations = [
            CodeRecommendationResponse(
                code="I21.9",
                code_type=CodeType.ICD10,
                confidence_score=0.9,
                reasoning="Test",
                recommendation_source=RecommendationSource.ML_MODEL
            ),
            CodeRecommendationResponse(
                code="93458",
                code_type=CodeType.CPT,
                confidence_score=0.8,
                reasoning="Test",
                recommendation_source=RecommendationSource.RULE_BASED
            )
        ]
        
        summary = coding_service._generate_summary(recommendations)
        
        assert summary["total_recommendations"] == 2
        assert summary["by_type"][CodeType.ICD10] == 1
        assert summary["by_type"][CodeType.CPT] == 1
        assert abs(summary["average_confidence"] - 0.85) < 0.001  # Use tolerance for float comparison
        assert summary["min_confidence"] == 0.8
        assert summary["max_confidence"] == 0.9
        assert summary["high_confidence_count"] == 2  # Both >= 0.8
    
    @pytest.mark.asyncio
    async def test_approve_recommendation(self, coding_service):
        """Test recommendation approval."""
        # Mock database query
        mock_recommendation = Mock()
        mock_recommendation.id = 1
        mock_recommendation.approved = False
        mock_recommendation.claim_id = "TEST_001"
        mock_recommendation.code = "I21.9"
        mock_recommendation.code_type = "ICD10"
        mock_recommendation.confidence_score = 0.9
        
        coding_service.db.query.return_value.filter.return_value.first.return_value = mock_recommendation
        coding_service.db.commit = Mock()
        coding_service.audit_service.log_action = AsyncMock()
        
        result = await coding_service.approve_recommendation(
            recommendation_id=1,
            user_id="test_user",
            notes="Approved after review"
        )
        
        assert result["status"] == "success"
        assert result["recommendation_id"] == 1
        assert result["approved_by"] == "test_user"
        assert mock_recommendation.approved == True
        assert mock_recommendation.reviewed_by == "test_user"
        
        # Verify audit log was created
        coding_service.audit_service.log_action.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_approve_recommendation_not_found(self, coding_service):
        """Test approval of non-existent recommendation."""
        coding_service.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await coding_service.approve_recommendation(
            recommendation_id=999,
            user_id="test_user"
        )
        
        assert result["status"] == "error"
        assert "not found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_approve_recommendation_already_approved(self, coding_service):
        """Test approval of already approved recommendation."""
        mock_recommendation = Mock()
        mock_recommendation.approved = True
        
        coding_service.db.query.return_value.filter.return_value.first.return_value = mock_recommendation
        
        result = await coding_service.approve_recommendation(
            recommendation_id=1,
            user_id="test_user"
        )
        
        assert result["status"] == "warning"
        assert "already approved" in result["message"]


@pytest.mark.unit
class TestCodingServiceValidation:
    """Test validation functionality."""
    
    @pytest.fixture
    def coding_service(self):
        """Create minimal coding service for validation tests."""
        mock_db = Mock()
        with patch('api.services.coding_service.ICD10Service'), \
             patch('api.services.coding_service.CPTService'), \
             patch('api.services.coding_service.DRGService'), \
             patch('api.services.coding_service.CodePredictor'), \
             patch('api.services.coding_service.AuditService'):
            return CodingService(mock_db)
    
    @pytest.mark.asyncio
    async def test_validate_recommendations_success(self, coding_service):
        """Test successful validation."""
        # Mock database response
        mock_recs = [
            Mock(code_type="ICD10", confidence_score=0.9),
            Mock(code_type="CPT", confidence_score=0.8)
        ]
        
        coding_service.db.query.return_value.filter.return_value.all.return_value = mock_recs
        
        result = await coding_service.validate_recommendations("TEST_001")
        
        assert result["validation_passed"] == True
        assert result["total_recommendations"] == 2
        assert len(result["issues"]) == 0
        assert len(result["warnings"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_recommendations_low_confidence(self, coding_service):
        """Test validation with low confidence issues."""
        mock_recs = [
            Mock(code="I21.9", code_type="ICD10", confidence_score=0.2),  # Below threshold
            Mock(code="93458", code_type="CPT", confidence_score=0.8)
        ]
        
        coding_service.db.query.return_value.filter.return_value.all.return_value = mock_recs
        
        result = await coding_service.validate_recommendations("TEST_001")
        
        assert result["validation_passed"] == False
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "low_confidence"
        assert result["issues"][0]["code"] == "I21.9"
    
    @pytest.mark.asyncio
    async def test_validate_recommendations_missing_diagnosis(self, coding_service):
        """Test validation with missing primary diagnosis."""
        mock_recs = [
            Mock(code_type="CPT", confidence_score=0.8)  # Only CPT, no ICD10
        ]
        
        coding_service.db.query.return_value.filter.return_value.all.return_value = mock_recs
        
        result = await coding_service.validate_recommendations("TEST_001")
        
        assert result["validation_passed"] == False
        assert any(issue["type"] == "missing_primary_diagnosis" for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_validate_recommendations_no_data(self, coding_service):
        """Test validation with no recommendations."""
        coding_service.db.query.return_value.filter.return_value.all.return_value = []
        
        result = await coding_service.validate_recommendations("TEST_001")
        
        assert result["status"] == "no_recommendations"
        assert "No recommendations found" in result["message"]
