"""
ML-based Code Predictor v0.2

Enhanced machine learning-based medical code predictions with improved 
confidence scoring and feature extraction.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import json
from collections import defaultdict

class CodePredictor:
    """
    Enhanced machine learning service for medical code prediction.
    
    Provides sophisticated ML-based recommendations for ICD-10, CPT, and DRG codes
    with improved confidence scoring and feature analysis.
    """
    
    def __init__(self):
        self.model_version = "v0.2.0"
        self._load_models()
        self._load_enhanced_patterns()
        self.prediction_history = []  # Store for model improvement
    
    def _load_models(self):
        """Load enhanced pre-trained models with improved pattern matching."""
        # In a real implementation, this would load trained neural networks
        # For v0.2, we're using enhanced rule-based patterns with ML-style scoring
        
        self.icd10_patterns = {
            'cardiovascular': {
                'patterns': ['chest pain', 'myocardial', 'cardiac', 'heart', 'angina', 
                           'arrhythmia', 'hypertension', 'palpitations', 'coronary'],
                'codes': ['I21.9', 'I25.9', 'I50.9', 'I10', 'I48.9'],
                'weights': [0.85, 0.75, 0.65, 0.90, 0.70],
                'context_boost': ['infarction', 'disease', 'failure', 'primary', 'atrial']
            },
            'respiratory': {
                'patterns': ['dyspnea', 'shortness of breath', 'COPD', 'pneumonia', 
                           'asthma', 'bronchitis', 'emphysema', 'respiratory'],
                'codes': ['J44.1', 'J18.9', 'R06.2', 'J45.9', 'J20.9'],
                'weights': [0.90, 0.80, 0.70, 0.85, 0.65],
                'context_boost': ['acute', 'chronic', 'exacerbation', 'distress']
            },
            'diabetes': {
                'patterns': ['diabetes', 'hyperglycemia', 'blood sugar', 'diabetic',
                           'glucose', 'insulin', 'hemoglobin a1c'],
                'codes': ['E11.9', 'E11.65', 'E11.40', 'E10.9', 'E11.22'],
                'weights': [0.90, 0.75, 0.70, 0.80, 0.65],
                'context_boost': ['type 2', 'type 1', 'mellitus', 'uncontrolled']
            },
            'renal': {
                'patterns': ['kidney', 'renal', 'dialysis', 'nephritis', 'nephropathy',
                           'uremia', 'creatinine', 'glomerular'],
                'codes': ['N18.6', 'N19', 'N03.9', 'N18.3', 'N25.9'],
                'weights': [0.85, 0.75, 0.70, 0.80, 0.60],
                'context_boost': ['chronic', 'acute', 'failure', 'disease']
            },
            'neurological': {
                'patterns': ['seizure', 'epilepsy', 'stroke', 'headache', 'migraine',
                           'dementia', 'parkinson', 'neuropathy'],
                'codes': ['G40.9', 'I63.9', 'G43.9', 'F03.90', 'G20'],
                'weights': [0.88, 0.82, 0.75, 0.70, 0.85],
                'context_boost': ['focal', 'generalized', 'ischemic', 'chronic']
            }
        }
        
        self.cpt_patterns = {
            'evaluation_management': {
                'patterns': ['office visit', 'consultation', 'evaluation', 'exam',
                           'assessment', 'follow-up', 'new patient', 'established'],
                'codes': ['99213', '99214', '99223', '99202', '99203'],
                'weights': [0.85, 0.75, 0.80, 0.90, 0.85],
                'context_boost': ['comprehensive', 'detailed', 'straightforward']
            },
            'procedures_surgery': {
                'patterns': ['surgery', 'procedure', 'operation', 'surgical',
                           'excision', 'repair', 'removal', 'insertion'],
                'codes': ['45378', '36415', '93010', '11042', '12001'],
                'weights': [0.80, 0.90, 0.85, 0.75, 0.70],
                'context_boost': ['laparoscopic', 'open', 'percutaneous']
            },
            'imaging_diagnostics': {
                'patterns': ['x-ray', 'CT', 'MRI', 'ultrasound', 'scan',
                           'radiograph', 'tomography', 'echo'],
                'codes': ['71020', '74150', '70553', '76700', '93306'],
                'weights': [0.90, 0.85, 0.80, 0.85, 0.75],
                'context_boost': ['with contrast', 'without contrast', 'complete']
            },
            'laboratory': {
                'patterns': ['blood test', 'lab', 'laboratory', 'panel',
                           'culture', 'biopsy', 'pathology'],
                'codes': ['80053', '85025', '87040', '88305'],
                'weights': [0.85, 0.80, 0.75, 0.70],
                'context_boost': ['comprehensive', 'basic', 'complete']
            }
        }
    
    def _load_enhanced_patterns(self):
        """Load enhanced pattern matching with medical terminology."""
        self.medical_specialties = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'coronary'],
            'pulmonology': ['lung', 'respiratory', 'pulmonary', 'breathing'],
            'endocrinology': ['diabetes', 'thyroid', 'hormone', 'endocrine'],
            'nephrology': ['kidney', 'renal', 'dialysis', 'urinary'],
            'neurology': ['brain', 'neurological', 'seizure', 'stroke']
        }
        
        self.severity_indicators = {
            'high': ['acute', 'severe', 'critical', 'emergency', 'urgent'],
            'moderate': ['moderate', 'symptomatic', 'stable', 'chronic'],
            'low': ['mild', 'minimal', 'resolved', 'improving']
        }
        
        self.clinical_context_patterns = {
            'admission': ['admitted', 'hospitalized', 'inpatient'],
            'discharge': ['discharged', 'released', 'outpatient'],
            'emergency': ['emergency', 'urgent', 'stat', 'immediate'],
            'routine': ['routine', 'scheduled', 'follow-up', 'regular']
        }
    
    async def predict_icd10_codes(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Enhanced ICD-10 code prediction with sophisticated confidence scoring.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of predicted codes with enhanced confidence metrics
        """
        predictions = []
        text_lower = clinical_text.lower()
        
        # Enhanced feature extraction
        clinical_features = self.extract_enhanced_clinical_features(text_lower)
        
        # Advanced pattern matching with context awareness
        for category, category_data in self.icd10_patterns.items():
            category_matches = self._analyze_category_matches(
                text_lower, category_data, clinical_features
            )
            
            if category_matches['score'] > 0:
                codes = category_data['codes']
                weights = category_data['weights']
                
                for i, code in enumerate(codes):
                    # Enhanced confidence calculation
                    base_confidence = weights[i]
                    context_boost = category_matches['context_boost']
                    feature_alignment = category_matches['feature_alignment']
                    
                    confidence = self._calculate_enhanced_confidence(
                        base_confidence, context_boost, feature_alignment, 
                        category_matches['pattern_strength']
                    )
                    
                    # Apply clinical context modifiers
                    confidence = self._apply_clinical_context(
                        confidence, clinical_features, category
                    )
                    
                    predictions.append({
                        'code': code,
                        'confidence': min(0.98, confidence),  # Cap at 98%
                        'features': category_matches['matched_patterns'],
                        'category': category,
                        'confidence_breakdown': {
                            'base_score': base_confidence,
                            'context_boost': context_boost,
                            'feature_alignment': feature_alignment,
                            'clinical_context': clinical_features['context_score']
                        },
                        'reasoning_factors': category_matches['reasoning_factors']
                    })
        
        # Sort by confidence and apply diversity filtering
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return self._apply_diversity_filter(predictions, max_results=5)
    
    async def predict_cpt_codes(self, clinical_text: str) -> List[Dict[str, Any]]:
        """
        Enhanced CPT code prediction with procedure-specific analysis.
        
        Args:
            clinical_text: Clinical documentation text
            
        Returns:
            List of predicted CPT codes with detailed confidence metrics
        """
        predictions = []
        text_lower = clinical_text.lower()
        
        # Enhanced feature extraction for procedures
        clinical_features = self.extract_enhanced_clinical_features(text_lower)
        procedure_features = self._extract_procedure_features(text_lower)
        
        # Analyze each CPT category
        for category, category_data in self.cpt_patterns.items():
            category_matches = self._analyze_category_matches(
                text_lower, category_data, clinical_features
            )
            
            if category_matches['score'] > 0:
                codes = category_data['codes']
                weights = category_data['weights']
                
                for i, code in enumerate(codes):
                    base_confidence = weights[i]
                    
                    # Procedure-specific confidence adjustments
                    procedure_confidence = self._calculate_procedure_confidence(
                        code, procedure_features, category_matches
                    )
                    
                    final_confidence = self._calculate_enhanced_confidence(
                        base_confidence,
                        category_matches['context_boost'],
                        procedure_confidence,
                        category_matches['pattern_strength']
                    )
                    
                    predictions.append({
                        'code': code,
                        'confidence': min(0.95, final_confidence),  # CPT slightly lower cap
                        'features': category_matches['matched_patterns'],
                        'category': category,
                        'procedure_indicators': procedure_features,
                        'confidence_breakdown': {
                            'base_score': base_confidence,
                            'procedure_alignment': procedure_confidence,
                            'context_boost': category_matches['context_boost'],
                            'pattern_strength': category_matches['pattern_strength']
                        },
                        'reasoning_factors': category_matches['reasoning_factors']
                    })
        
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return self._apply_diversity_filter(predictions, max_results=3)
    
    def _extract_procedure_features(self, text: str) -> Dict[str, Any]:
        """
        Extract procedure-specific features from clinical text.
        """
        features = {
            'procedure_verbs': [],
            'anatomical_sites': [],
            'technique_modifiers': [],
            'complexity_indicators': [],
            'duration_indicators': []
        }
        
        # Procedure action verbs
        procedure_verbs = [
            'performed', 'completed', 'underwent', 'excised', 'repaired',
            'removed', 'inserted', 'biopsied', 'scanned', 'examined'
        ]
        features['procedure_verbs'] = [verb for verb in procedure_verbs if verb in text]
        
        # Anatomical procedure sites
        anatomical_sites = [
            'cardiac', 'pulmonary', 'abdominal', 'thoracic', 'pelvic',
            'cranial', 'spinal', 'vascular', 'hepatic', 'renal'
        ]
        features['anatomical_sites'] = [site for site in anatomical_sites if site in text]
        
        # Technique modifiers
        techniques = [
            'laparoscopic', 'endoscopic', 'percutaneous', 'open',
            'minimally invasive', 'robotic', 'stereotactic'
        ]
        features['technique_modifiers'] = [tech for tech in techniques if tech in text]
        
        # Complexity indicators
        complexity = ['simple', 'complex', 'extensive', 'limited', 'comprehensive']
        features['complexity_indicators'] = [comp for comp in complexity if comp in text]
        
        return features
    
    def _calculate_procedure_confidence(
        self, 
        cpt_code: str, 
        procedure_features: Dict, 
        category_matches: Dict
    ) -> float:
        """
        Calculate procedure-specific confidence adjustments.
        """
        confidence_boost = 0.0
        
        # Procedure verb presence
        if procedure_features['procedure_verbs']:
            confidence_boost += 0.15
        
        # Anatomical site specificity
        if procedure_features['anatomical_sites']:
            confidence_boost += 0.10
        
        # Technique modifier alignment
        if procedure_features['technique_modifiers']:
            confidence_boost += 0.08
        
        # Complexity indicators
        if procedure_features['complexity_indicators']:
            confidence_boost += 0.05
        
        return min(0.4, confidence_boost)
    
    async def predict_codes_batch(
        self, 
        clinical_texts: List[str],
        include_confidence_analysis: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch processing for multiple clinical texts.
        
        Args:
            clinical_texts: List of clinical documentation texts
            include_confidence_analysis: Include detailed confidence analysis
            
        Returns:
            List of prediction results for each text
        """
        batch_results = []
        
        for i, text in enumerate(clinical_texts):
            try:
                # Generate predictions for both ICD-10 and CPT
                icd10_predictions = await self.predict_icd10_codes(text)
                cpt_predictions = await self.predict_cpt_codes(text)
                
                result = {
                    'batch_index': i,
                    'text_length': len(text),
                    'icd10_predictions': icd10_predictions,
                    'cpt_predictions': cpt_predictions,
                    'processing_timestamp': self._get_timestamp()
                }
                
                if include_confidence_analysis:
                    result['confidence_analysis'] = self._analyze_batch_confidence(
                        icd10_predictions, cpt_predictions
                    )
                
                batch_results.append(result)
                
            except Exception as e:
                batch_results.append({
                    'batch_index': i,
                    'error': str(e),
                    'processing_timestamp': self._get_timestamp()
                })
        
        return batch_results
    
    def _analyze_batch_confidence(
        self, 
        icd10_preds: List[Dict], 
        cpt_preds: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze confidence metrics for batch processing.
        """
        all_confidences = [p['confidence'] for p in icd10_preds + cpt_preds]
        
        if not all_confidences:
            return {'status': 'no_predictions'}
        
        return {
            'average_confidence': sum(all_confidences) / len(all_confidences),
            'min_confidence': min(all_confidences),
            'max_confidence': max(all_confidences),
            'high_confidence_count': len([c for c in all_confidences if c >= 0.8]),
            'prediction_count': len(all_confidences),
            'confidence_distribution': {
                'high': len([c for c in all_confidences if c >= 0.8]),
                'medium': len([c for c in all_confidences if 0.5 <= c < 0.8]),
                'low': len([c for c in all_confidences if c < 0.5])
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for tracking."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def store_prediction_feedback(
        self, 
        prediction_id: str, 
        actual_codes: List[str], 
        feedback_score: float
    ) -> None:
        """
        Store feedback for model improvement.
        
        Args:
            prediction_id: Unique identifier for the prediction
            actual_codes: Actual codes that were used
            feedback_score: Quality score from 0-1
        """
        feedback_entry = {
            'prediction_id': prediction_id,
            'actual_codes': actual_codes,
            'feedback_score': feedback_score,
            'timestamp': self._get_timestamp(),
            'model_version': self.model_version
        }
        
        self.prediction_history.append(feedback_entry)
        
        # Keep only recent feedback (last 1000 entries)
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-1000:]
    
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
    
    def extract_enhanced_clinical_features(self, text: str) -> Dict[str, Any]:
        """
        Enhanced clinical feature extraction with medical context analysis.
        
        Args:
            text: Clinical text (already lowercased)
            
        Returns:
            Comprehensive feature dictionary
        """
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(text.split('.')),
            'medical_terms': [],
            'procedures_mentioned': [],
            'symptoms_mentioned': [],
            'medications_mentioned': [],
            'specialty_indicators': {},
            'severity_level': 'moderate',
            'clinical_context': 'routine',
            'context_score': 0.5,
            'temporal_indicators': [],
            'anatomical_references': []
        }
        
        # Medical specialty detection
        for specialty, keywords in self.medical_specialties.items():
            matches = [kw for kw in keywords if kw in text]
            if matches:
                features['specialty_indicators'][specialty] = len(matches)
        
        # Severity assessment
        severity_scores = {'high': 0, 'moderate': 0, 'low': 0}
        for level, indicators in self.severity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            severity_scores[level] = score
        
        features['severity_level'] = max(severity_scores, key=severity_scores.get)
        
        # Clinical context determination
        context_scores = defaultdict(int)
        for context_type, patterns in self.clinical_context_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            context_scores[context_type] = score
        
        if context_scores:
            features['clinical_context'] = max(context_scores, key=context_scores.get)
            features['context_score'] = max(context_scores.values()) / 10.0
        
        # Temporal indicators
        temporal_patterns = ['acute', 'chronic', 'recent', 'ongoing', 'past', 'current']
        features['temporal_indicators'] = [tp for tp in temporal_patterns if tp in text]
        
        # Anatomical references
        anatomical_terms = ['chest', 'abdomen', 'head', 'limb', 'back', 'neck', 'pelvis']
        features['anatomical_references'] = [at for at in anatomical_terms if at in text]
        
        return features
    
    def _analyze_category_matches(
        self, 
        text: str, 
        category_data: Dict, 
        clinical_features: Dict
    ) -> Dict[str, Any]:
        """
        Analyze pattern matches for a specific category with context awareness.
        """
        matched_patterns = []
        pattern_strength = 0
        reasoning_factors = []
        
        # Primary pattern matching
        for pattern in category_data['patterns']:
            if pattern in text:
                matched_patterns.append(pattern)
                frequency = text.count(pattern)
                pattern_strength += frequency * 0.15
                reasoning_factors.append(f"Found '{pattern}' {frequency} time(s)")
        
        # Context boost evaluation
        context_boost = 0
        if 'context_boost' in category_data:
            for boost_term in category_data['context_boost']:
                if boost_term in text:
                    context_boost += 0.1
                    reasoning_factors.append(f"Context boost from '{boost_term}'")
        
        # Feature alignment scoring
        feature_alignment = self._calculate_feature_alignment(
            matched_patterns, clinical_features
        )
        
        total_score = pattern_strength + context_boost + feature_alignment
        
        return {
            'score': total_score,
            'matched_patterns': matched_patterns,
            'context_boost': context_boost,
            'feature_alignment': feature_alignment,
            'pattern_strength': pattern_strength,
            'reasoning_factors': reasoning_factors
        }
    
    def _calculate_enhanced_confidence(
        self, 
        base_confidence: float,
        context_boost: float,
        feature_alignment: float,
        pattern_strength: float
    ) -> float:
        """
        Calculate enhanced confidence score using multiple factors.
        """
        # Weighted combination of factors
        confidence = (
            base_confidence * 0.4 +  # Base pattern weight
            context_boost * 0.2 +    # Context enhancement
            feature_alignment * 0.2 + # Feature alignment
            pattern_strength * 0.2   # Pattern strength
        )
        
        # Apply diminishing returns for very high scores
        if confidence > 0.85:
            confidence = 0.85 + (confidence - 0.85) * 0.5
        
        return min(0.98, confidence)
    
    def _apply_clinical_context(
        self, 
        confidence: float, 
        clinical_features: Dict, 
        category: str
    ) -> float:
        """
        Apply clinical context modifiers to confidence score.
        """
        # Severity modifier
        if clinical_features['severity_level'] == 'high':
            confidence *= 1.1
        elif clinical_features['severity_level'] == 'low':
            confidence *= 0.9
        
        # Specialty alignment bonus
        if category in clinical_features['specialty_indicators']:
            specialty_score = clinical_features['specialty_indicators'][category]
            confidence += specialty_score * 0.05
        
        # Context type modifier
        if clinical_features['clinical_context'] == 'emergency':
            confidence *= 1.05
        
        return min(0.98, confidence)
    
    def _calculate_feature_alignment(
        self, 
        matched_patterns: List[str], 
        clinical_features: Dict
    ) -> float:
        """
        Calculate how well patterns align with overall clinical features.
        """
        if not matched_patterns:
            return 0.0
        
        alignment_score = 0.0
        
        # Temporal alignment
        if clinical_features['temporal_indicators']:
            alignment_score += 0.1
        
        # Anatomical alignment
        if clinical_features['anatomical_references']:
            alignment_score += 0.1
        
        # Specialty alignment
        if clinical_features['specialty_indicators']:
            alignment_score += 0.15
        
        return min(0.3, alignment_score)
    
    def _apply_diversity_filter(
        self, 
        predictions: List[Dict], 
        max_results: int = 5
    ) -> List[Dict]:
        """
        Apply diversity filtering to ensure varied recommendations.
        """
        if len(predictions) <= max_results:
            return predictions
        
        filtered = []
        used_categories = set()
        
        # First, add highest confidence from each category
        for pred in predictions:
            if pred['category'] not in used_categories:
                filtered.append(pred)
                used_categories.add(pred['category'])
                if len(filtered) >= max_results:
                    break
        
        # Fill remaining slots with highest confidence overall
        remaining_slots = max_results - len(filtered)
        for pred in predictions:
            if pred not in filtered and remaining_slots > 0:
                filtered.append(pred)
                remaining_slots -= 1
        
        return filtered
    
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
