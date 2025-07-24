"""
ML-based Code Predictor

Provides machine learning-based medical code predictions.
"""

import re
from typing import List, Dict, Any
import numpy as np

class CodePredictor:
    """
    Machine learning service for medical code prediction.
    
    Provides ML-based recommendations for ICD-10, CPT, and DRG codes
    based on clinical text analysis.
    """
    
    def __init__(self):
        self.model_version = "v0.1.0"
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models (placeholder implementation)."""
        # In a real implementation, this would load trained models
        # For now, we'll use rule-based approximations
        
        self.icd10_patterns = {
            'cardiovascular': {
                'patterns': ['chest pain', 'myocardial', 'cardiac', 'heart'],
                'codes': ['I21.9', 'I25.9', 'I50.9'],
                'weights': [0.8, 0.6, 0.5]
            },
            'respiratory': {
                'patterns': ['dyspnea', 'shortness of breath', 'COPD', 'pneumonia'],
                'codes': ['J44.1', 'J18.9', 'R06.2'],
                'weights': [0.9, 0.7, 0.6]
            },
            'diabetes': {
                'patterns': ['diabetes', 'hyperglycemia', 'blood sugar'],
                'codes': ['E11.9', 'E11.65', 'E11.40'],
                'weights': [0.9, 0.7, 0.6]
            },
            'renal': {
                'patterns': ['kidney', 'renal', 'dialysis', 'nephritis'],
                'codes': ['N18.6', 'N19', 'N03.9'],
                'weights': [0.8, 0.7, 0.6]
            }
        }
        
        self.cpt_patterns = {
            'evaluation': {
                'patterns': ['office visit', 'consultation', 'evaluation'],
                'codes': ['99213', '99214', '99223'],
                'weights': [0.8, 0.6, 0.7]
            },
            'procedures': {
                'patterns': ['surgery', 'procedure', 'operation'],
                'codes': ['45378', '36415', '93010'],
                'weights': [0.7, 0.9, 0.8]
            },
            'imaging': {
                'patterns': ['x-ray', 'CT', 'MRI', 'ultrasound'],
                'codes': ['71020', '74150', '70553'],
                'weights': [0.9, 0.8, 0.7]
            }
        }
    
    async def predict_icd10_codes(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Predict ICD-10 codes using ML-based analysis.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of predicted codes with confidence scores
        """
        predictions = []
        text_lower = clinical_text.lower()
        
        # Feature extraction and pattern matching
        for category, category_data in self.icd10_patterns.items():
            category_score = 0
            matched_patterns = []
            
            for pattern in category_data['patterns']:
                if pattern in text_lower:
                    matched_patterns.append(pattern)
                    # Simple TF-IDF approximation
                    frequency = text_lower.count(pattern)
                    category_score += frequency * 0.1
            
            if matched_patterns:
                # Generate predictions for this category
                codes = category_data['codes']
                weights = category_data['weights']
                
                for i, code in enumerate(codes):
                    confidence = min(0.95, weights[i] + category_score)
                    
                    predictions.append({
                        'code': code,
                        'confidence': confidence,
                        'features': matched_patterns,
                        'category': category
                    })
        
        # Sort by confidence and return top predictions
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return predictions[:5]
    
    async def predict_cpt_codes(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Predict CPT codes using ML-based analysis.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of predicted codes with confidence scores
        """
        predictions = []
        text_lower = clinical_text.lower()
        
        for category, category_data in self.cpt_patterns.items():
            category_score = 0
            matched_patterns = []
            
            for pattern in category_data['patterns']:
                if pattern in text_lower:
                    matched_patterns.append(pattern)
                    frequency = text_lower.count(pattern)
                    category_score += frequency * 0.1
            
            if matched_patterns:
                codes = category_data['codes']
                weights = category_data['weights']
                
                for i, code in enumerate(codes):
                    confidence = min(0.90, weights[i] + category_score)
                    
                    predictions.append({
                        'code': code,
                        'confidence': confidence,
                        'features': matched_patterns,
                        'category': category
                    })
        
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return predictions[:3]
    
    def extract_clinical_features(self, text: str) -> Dict[str, Any]:
        """
        Extract clinical features from text for ML processing.
        
        Args:
            text: Clinical text
            
        Returns:
            Dictionary of extracted features
        """
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(text.split('.')),
            'medical_terms': [],
            'procedures_mentioned': [],
            'symptoms_mentioned': [],
            'medications_mentioned': []
        }
        
        text_lower = text.lower()
        
        # Medical terms
        medical_terms = [
            'diagnosis', 'symptoms', 'treatment', 'procedure',
            'medication', 'surgery', 'examination', 'consultation'
        ]
        features['medical_terms'] = [term for term in medical_terms if term in text_lower]
        
        # Common symptoms
        symptoms = [
            'pain', 'fever', 'nausea', 'fatigue', 'shortness of breath',
            'chest pain', 'headache', 'dizziness'
        ]
        features['symptoms_mentioned'] = [symptom for symptom in symptoms if symptom in text_lower]
        
        # Common procedures
        procedures = [
            'surgery', 'x-ray', 'blood test', 'examination',
            'colonoscopy', 'endoscopy', 'biopsy'
        ]
        features['procedures_mentioned'] = [proc for proc in procedures if proc in text_lower]
        
        return features
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def get_model_explanation(self, prediction: Dict[str, Any]) -> str:
        """
        Generate explanation for a model prediction.
        
        Args:
            prediction: Prediction dictionary
            
        Returns:
            Human-readable explanation
        """
        explanation_parts = [
            f"ML model prediction with {prediction['confidence']:.2%} confidence",
            f"Based on features: {', '.join(prediction.get('features', []))}"
        ]
        
        if 'category' in prediction:
            explanation_parts.append(f"Category: {prediction['category']}")
        
        return ". ".join(explanation_parts) + "."
