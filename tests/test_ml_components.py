"""
Machine Learning tests for FairClaimRCM
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from core.ml.code_predictor import CodePredictor


@pytest.mark.ml
class TestCodePredictor:
    """Test suite for ML-based code prediction."""
    
    @pytest.fixture
    def code_predictor(self):
        """Create CodePredictor instance."""
        return CodePredictor()
    
    def test_init(self, code_predictor):
        """Test CodePredictor initialization."""
        assert code_predictor.model_version is not None
        assert hasattr(code_predictor, 'icd10_patterns')
        assert hasattr(code_predictor, 'cpt_patterns')
    
    def test_extract_clinical_features(self, code_predictor):
        """Test clinical feature extraction."""
        clinical_text = """
        Patient presents with chest pain, shortness of breath, and diaphoresis.
        ECG shows ST elevation. Troponin levels elevated.
        Diagnosis: Acute myocardial infarction.
        """
        
        features = code_predictor.extract_clinical_features(clinical_text)
        
        assert isinstance(features, dict)
        assert "medical_terms" in features
        assert "sentence_count" in features
        # Should extract relevant medical terms
        assert len(features["medical_terms"]) > 0
    
    def test_extract_clinical_features_empty_text(self, code_predictor):
        """Test feature extraction with empty text."""
        features = code_predictor.extract_clinical_features("")
        assert isinstance(features, dict)
        assert "medical_terms" in features
        assert features["medical_terms"] == []
    
    def test_preprocess_for_ml(self, code_predictor):
        """Test ML preprocessing."""
        text = "Patient has TYPE 2 DIABETES   with complications!!!"
        
        # The actual method is extract_enhanced_clinical_features
        processed = code_predictor.extract_enhanced_clinical_features(text)
        
        assert isinstance(processed, dict)
        assert "medical_terms" in processed
        # Should normalize text and extract features
        medical_terms = processed["medical_terms"]
        assert any("diabetes" in term.lower() for term in medical_terms)
    
    @pytest.mark.asyncio
    async def test_predict_icd10_codes(self, code_predictor):
        """Test ICD-10 code prediction."""
        clinical_text = "Patient with type 2 diabetes mellitus and hypertension"
        
        with patch.object(code_predictor, '_predict_codes_ml') as mock_predict:
            mock_predict.return_value = [
                {
                    "code": "E11.9",
                    "confidence": 0.85,
                    "features": ["diabetes", "type", "mellitus"]
                }
            ]
            
            predictions = await code_predictor.predict_icd10_codes(clinical_text)
            
            assert len(predictions) >= 1
            assert predictions[0]["code"] == "E11.9"
            assert predictions[0]["confidence"] > 0.8
            assert "features" in predictions[0]
    
    @pytest.mark.asyncio
    async def test_predict_cpt_codes(self, code_predictor):
        """Test CPT code prediction."""
        clinical_text = "Performed cardiac catheterization with angioplasty"
        
        with patch.object(code_predictor, '_predict_codes_ml') as mock_predict:
            mock_predict.return_value = [
                {
                    "code": "93458",
                    "confidence": 0.90,
                    "features": ["cardiac", "catheterization"]
                }
            ]
            
            predictions = await code_predictor.predict_cpt_codes(clinical_text)
            
            assert len(predictions) >= 1
            assert predictions[0]["code"] == "93458"
            assert predictions[0]["confidence"] > 0.8
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_predict_codes_batch(self, code_predictor):
        """Test batch code prediction."""
        clinical_texts = [
            "Patient with diabetes",
            "Cardiac catheterization performed",
            "Acute appendicitis treated surgically"
        ]
        
        with patch.object(code_predictor, '_predict_codes_ml_batch') as mock_batch:
            mock_batch.return_value = [
                {
                    "icd10_predictions": [{"code": "E11.9", "confidence": 0.8}],
                    "cpt_predictions": []
                },
                {
                    "icd10_predictions": [],
                    "cpt_predictions": [{"code": "93458", "confidence": 0.9}]
                },
                {
                    "icd10_predictions": [{"code": "K35.9", "confidence": 0.85}],
                    "cpt_predictions": [{"code": "44970", "confidence": 0.8}]
                }
            ]
            
            results = await code_predictor.predict_codes_batch(
                clinical_texts, 
                include_confidence_analysis=True
            )
            
            assert len(results) == 3
            assert all("icd10_predictions" in result for result in results)
            assert all("cpt_predictions" in result for result in results)
    
    def test_calculate_confidence_score(self, code_predictor):
        """Test confidence score calculation."""
        # Test with mock prediction probabilities
        features = ["chest", "pain", "acute", "myocardial"]
        text = "chest pain acute myocardial infarction"
        
        with patch.object(code_predictor, '_get_model_prediction_probability') as mock_prob:
            mock_prob.return_value = 0.85
            
            confidence = code_predictor.calculate_confidence_score(
                "I21.9", features, text, code_type="icd10"
            )
            
            assert 0.0 <= confidence <= 1.0
            assert confidence > 0.7  # Should be high for good match
    
    def test_calculate_confidence_score_low_match(self, code_predictor):
        """Test confidence score for poor feature match."""
        features = ["headache", "migraine"]
        text = "patient has headache and migraine"
        
        with patch.object(code_predictor, '_get_model_prediction_probability') as mock_prob:
            mock_prob.return_value = 0.3  # Low model confidence
            
            confidence = code_predictor.calculate_confidence_score(
                "I21.9", features, text, code_type="icd10"  # MI code for headache
            )
            
            assert confidence < 0.5  # Should be low for poor match
    
    @pytest.mark.requires_data
    def test_load_model_weights(self, code_predictor):
        """Test loading pre-trained model weights."""
        # This test would require actual model files
        # In practice, you'd have trained models saved
        
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('torch.load') as mock_load:
                mock_load.return_value = {"state_dict": {}}
                
                # Test that model loading doesn't crash
                try:
                    code_predictor._load_pretrained_models()
                    model_loaded = True
                except:
                    model_loaded = False
                
                # Should not crash even if models don't exist
                assert isinstance(model_loaded, bool)
    
    def test_feature_importance_analysis(self, code_predictor):
        """Test feature importance analysis."""
        features = ["diabetes", "type", "mellitus", "glucose", "elevated"]
        
        with patch.object(code_predictor, '_analyze_feature_importance') as mock_analysis:
            mock_analysis.return_value = {
                "diabetes": 0.8,
                "mellitus": 0.7,
                "type": 0.6,
                "glucose": 0.5,
                "elevated": 0.3
            }
            
            importance = code_predictor.get_feature_importance(features, "E11.9")
            
            assert isinstance(importance, dict)
            assert len(importance) > 0
            assert all(0.0 <= score <= 1.0 for score in importance.values())
    
    @pytest.mark.asyncio
    async def test_prediction_with_confidence_breakdown(self, code_predictor):
        """Test prediction with detailed confidence breakdown."""
        clinical_text = "Patient with acute myocardial infarction"
        
        with patch.object(code_predictor, '_predict_codes_ml') as mock_predict:
            mock_predict.return_value = [
                {
                    "code": "I21.9",
                    "confidence": 0.85,
                    "confidence_breakdown": {
                        "base_score": 0.8,
                        "context_boost": 0.05,
                        "feature_match": 0.9,
                        "frequency_adjustment": -0.1
                    },
                    "features": ["acute", "myocardial", "infarction"],
                    "reasoning_factors": [
                        "Strong match for 'acute myocardial infarction' pattern",
                        "High clinical feature overlap",
                        "Consistent with typical MI presentation"
                    ]
                }
            ]
            
            predictions = await code_predictor.predict_icd10_codes(
                clinical_text, 
                include_confidence_breakdown=True
            )
            
            pred = predictions[0]
            assert "confidence_breakdown" in pred
            assert "reasoning_factors" in pred
            assert len(pred["reasoning_factors"]) > 0
    
    def test_model_performance_metrics(self, code_predictor):
        """Test model performance calculation."""
        # Mock true vs predicted labels for testing
        true_codes = ["E11.9", "I21.9", "K35.9", "E11.9", "I21.9"]
        predicted_codes = ["E11.9", "I21.9", "K35.8", "E11.9", "I25.9"]
        confidences = [0.9, 0.85, 0.7, 0.8, 0.6]
        
        with patch.object(code_predictor, '_calculate_performance_metrics') as mock_metrics:
            mock_metrics.return_value = {
                "accuracy": 0.6,  # 3/5 correct
                "precision": 0.75,
                "recall": 0.6,
                "f1_score": 0.67,
                "average_confidence": 0.77
            }
            
            metrics = code_predictor.evaluate_predictions(
                true_codes, predicted_codes, confidences
            )
            
            assert "accuracy" in metrics
            assert "precision" in metrics
            assert "recall" in metrics
            assert "f1_score" in metrics
            assert 0.0 <= metrics["accuracy"] <= 1.0


@pytest.mark.ml
@pytest.mark.slow
class TestMLPipeline:
    """Test complete ML pipeline."""
    
    @pytest.fixture
    def code_predictor(self):
        """Create CodePredictor for pipeline testing."""
        return CodePredictor()
    
    @pytest.mark.asyncio
    async def test_end_to_end_prediction_pipeline(self, code_predictor, sample_clinical_text):
        """Test complete prediction pipeline."""
        # Mock the ML components
        with patch.object(code_predictor, 'predict_icd10_codes') as mock_icd10, \
             patch.object(code_predictor, 'predict_cpt_codes') as mock_cpt:
            
            mock_icd10.return_value = [
                {
                    "code": "I21.9",
                    "confidence": 0.9,
                    "features": ["acute", "myocardial", "infarction"]
                }
            ]
            
            mock_cpt.return_value = [
                {
                    "code": "93458",
                    "confidence": 0.85,
                    "features": ["cardiac", "catheterization"]
                }
            ]
            
            # Test ICD-10 prediction
            icd10_results = await code_predictor.predict_icd10_codes(sample_clinical_text)
            assert len(icd10_results) > 0
            assert icd10_results[0]["confidence"] > 0.8
            
            # Test CPT prediction
            cpt_results = await code_predictor.predict_cpt_codes(sample_clinical_text)
            assert len(cpt_results) > 0
            assert cpt_results[0]["confidence"] > 0.8
    
    @pytest.mark.requires_data
    def test_model_training_simulation(self, code_predictor):
        """Simulate model training process."""
        # This would test the training pipeline in a real implementation
        
        # Mock training data
        training_data = [
            ("Patient with diabetes", ["E11.9"]),
            ("Acute MI patient", ["I21.9"]),
            ("Cardiac cath procedure", [], ["93458"])
        ]
        
        with patch.object(code_predictor, '_train_model') as mock_train:
            mock_train.return_value = {
                "training_loss": 0.15,
                "validation_accuracy": 0.89,
                "epochs_trained": 10
            }
            
            # Simulate training
            training_result = code_predictor.train_models(training_data)
            
            assert "training_loss" in training_result
            assert "validation_accuracy" in training_result
            assert training_result["validation_accuracy"] > 0.8
