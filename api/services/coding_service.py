"""
Coding Service for FairClaimRCM

Provides medical coding recommendations using rule-based and ML approaches.
"""

import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from api.models.database import CodeRecommendation as CodeRecommendationModel, AuditLog
from api.models.schemas import (
    CodeRecommendationResponse, CodingResponse, CodeType, RecommendationSource
)
from core.terminology.icd10_service import ICD10Service
from core.terminology.cpt_service import CPTService
from core.terminology.drg_service import DRGService
from core.ml.code_predictor import CodePredictor
from api.services.audit_service import AuditService

class CodingService:
    """
    Main service for generating medical code recommendations.
    
    Combines rule-based and ML-based approaches to suggest appropriate
    ICD-10, CPT, and DRG codes for clinical documentation.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.icd10_service = ICD10Service()
        self.cpt_service = CPTService()
        self.drg_service = DRGService()
        self.code_predictor = CodePredictor()
        self.audit_service = AuditService(db)
    
    async def generate_recommendations(
        self,
        claim_id: str,
        clinical_text: str,
        include_explanations: bool = True
    ) -> CodingResponse:
        """
        Generate comprehensive coding recommendations for clinical text.
        
        Args:
            claim_id: Unique claim identifier
            clinical_text: Clinical documentation to analyze
            include_explanations: Whether to include detailed reasoning
            
        Returns:
            CodingResponse with recommendations and audit information
        """
        recommendations = []
        
        # Pre-process clinical text
        processed_text = self._preprocess_text(clinical_text)
        
        # Generate ICD-10 recommendations
        icd10_recs = await self._generate_icd10_recommendations(
            processed_text, include_explanations
        )
        recommendations.extend(icd10_recs)
        
        # Generate CPT recommendations
        cpt_recs = await self._generate_cpt_recommendations(
            processed_text, include_explanations
        )
        recommendations.extend(cpt_recs)
        
        # Generate DRG recommendations based on ICD-10 codes
        if icd10_recs:
            primary_icd10 = icd10_recs[0].code if icd10_recs else None
            drg_recs = await self._generate_drg_recommendations(
                primary_icd10, [rec.code for rec in icd10_recs], include_explanations
            )
            recommendations.extend(drg_recs)
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in recommendations:
            db_rec = CodeRecommendationModel(
                claim_id=claim_id,
                code=rec.code,
                code_type=rec.code_type,
                confidence_score=rec.confidence_score,
                reasoning=rec.reasoning,
                recommendation_source=rec.recommendation_source,
                model_version="v0.1.0"
            )
            self.db.add(db_rec)
            saved_recommendations.append(db_rec)
        
        self.db.commit()
        
        # Create audit log
        audit_log = await self.audit_service.log_action(
            claim_id=claim_id,
            action="coding_recommendations_generated",
            details={
                "text_length": len(clinical_text),
                "num_recommendations": len(recommendations),
                "recommendation_types": [rec.code_type for rec in recommendations],
                "confidence_scores": [rec.confidence_score for rec in recommendations]
            },
            user_id="system"
        )
        
        # Generate summary statistics
        summary = self._generate_summary(recommendations)
        
        return CodingResponse(
            recommendations=recommendations,
            summary=summary,
            audit_id=audit_log.id
        )
    
    async def _generate_icd10_recommendations(
        self, 
        clinical_text: str, 
        include_explanations: bool
    ) -> List[CodeRecommendationResponse]:
        """Generate ICD-10 diagnosis code recommendations."""
        recommendations = []
        
        # Rule-based recommendations
        rule_based = await self.icd10_service.find_codes_by_text(clinical_text)
        
        # ML-based recommendations
        ml_based = await self.code_predictor.predict_icd10_codes(clinical_text)
        
        # Combine and rank recommendations
        combined_codes = self._combine_recommendations(rule_based, ml_based)
        
        for code_data in combined_codes[:5]:  # Top 5 recommendations
            explanation = ""
            if include_explanations:
                explanation = self._generate_icd10_explanation(
                    code_data["code"], clinical_text, code_data
                )
            
            recommendations.append(CodeRecommendationResponse(
                code=code_data["code"],
                code_type=CodeType.ICD10,
                confidence_score=code_data["confidence"],
                reasoning=explanation,
                recommendation_source=code_data["source"]
            ))
        
        return recommendations
    
    async def _generate_cpt_recommendations(
        self, 
        clinical_text: str, 
        include_explanations: bool
    ) -> List[CodeRecommendationResponse]:
        """Generate CPT procedure code recommendations."""
        recommendations = []
        
        # Extract procedure mentions from text
        procedure_keywords = self._extract_procedure_keywords(clinical_text)
        
        if procedure_keywords:
            # Rule-based lookup
            rule_based = await self.cpt_service.find_codes_by_keywords(procedure_keywords)
            
            # ML-based recommendations
            ml_based = await self.code_predictor.predict_cpt_codes(clinical_text)
            
            # Combine recommendations
            combined_codes = self._combine_recommendations(rule_based, ml_based)
            
            for code_data in combined_codes[:3]:  # Top 3 recommendations
                explanation = ""
                if include_explanations:
                    explanation = self._generate_cpt_explanation(
                        code_data["code"], clinical_text, code_data
                    )
                
                recommendations.append(CodeRecommendationResponse(
                    code=code_data["code"],
                    code_type=CodeType.CPT,
                    confidence_score=code_data["confidence"],
                    reasoning=explanation,
                    recommendation_source=code_data["source"]
                ))
        
        return recommendations
    
    async def _generate_drg_recommendations(
        self, 
        primary_icd10: Optional[str],
        all_icd10_codes: List[str],
        include_explanations: bool
    ) -> List[CodeRecommendationResponse]:
        """Generate DRG recommendations based on ICD-10 codes."""
        recommendations = []
        
        if primary_icd10:
            drg_data = await self.drg_service.find_drg_by_diagnosis(
                primary_icd10, all_icd10_codes
            )
            
            if drg_data:
                explanation = ""
                if include_explanations:
                    explanation = self._generate_drg_explanation(
                        drg_data["code"], primary_icd10, all_icd10_codes
                    )
                
                recommendations.append(CodeRecommendationResponse(
                    code=drg_data["code"],
                    code_type=CodeType.DRG,
                    confidence_score=drg_data["confidence"],
                    reasoning=explanation,
                    recommendation_source=RecommendationSource.RULE_BASED
                ))
        
        return recommendations
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess clinical text."""
        # Remove PHI patterns (basic implementation)
        # In production, use proper PHI detection
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)  # SSN
        text = re.sub(r'\b\d{10,}\b', '[PHONE]', text)  # Phone numbers
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_procedure_keywords(self, text: str) -> List[str]:
        """Extract procedure-related keywords from clinical text."""
        procedure_patterns = [
            r'performed\s+(\w+)',
            r'underwent\s+(\w+)',
            r'procedure:\s*(\w+)',
            r'surgery:\s*(\w+)',
            r'operation:\s*(\w+)'
        ]
        
        keywords = []
        for pattern in procedure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))  # Remove duplicates
    
    def _combine_recommendations(
        self, 
        rule_based: List[Dict], 
        ml_based: List[Dict]
    ) -> List[Dict]:
        """Combine and rank rule-based and ML recommendations."""
        # Simple combination strategy - can be enhanced
        all_recommendations = {}
        
        # Add rule-based recommendations
        for rec in rule_based:
            code = rec["code"]
            all_recommendations[code] = {
                "code": code,
                "confidence": rec["confidence"] * 0.8,  # Slight penalty for rule-based
                "source": RecommendationSource.RULE_BASED,
                "rule_match": rec.get("match_reason", "")
            }
        
        # Add ML recommendations (higher weight)
        for rec in ml_based:
            code = rec["code"]
            if code in all_recommendations:
                # Boost confidence if both methods agree
                all_recommendations[code]["confidence"] = min(
                    1.0, 
                    all_recommendations[code]["confidence"] + rec["confidence"] * 0.3
                )
                all_recommendations[code]["source"] = RecommendationSource.HYBRID
            else:
                all_recommendations[code] = {
                    "code": code,
                    "confidence": rec["confidence"],
                    "source": RecommendationSource.ML_MODEL,
                    "ml_features": rec.get("features", [])
                }
        
        # Sort by confidence score
        return sorted(
            all_recommendations.values(), 
            key=lambda x: x["confidence"], 
            reverse=True
        )
    
    def _generate_icd10_explanation(
        self, 
        code: str, 
        clinical_text: str, 
        code_data: Dict
    ) -> str:
        """Generate human-readable explanation for ICD-10 recommendation."""
        description = self.icd10_service.get_code_description(code)
        
        explanation_parts = [
            f"Recommended ICD-10 code {code}: {description}",
            f"Confidence: {code_data['confidence']:.2%}",
            f"Source: {code_data['source']}"
        ]
        
        if code_data["source"] == RecommendationSource.RULE_BASED:
            explanation_parts.append(f"Match reason: {code_data.get('rule_match', 'Pattern match')}")
        elif code_data["source"] == RecommendationSource.ML_MODEL:
            features = code_data.get('ml_features', [])
            if features:
                explanation_parts.append(f"Key indicators: {', '.join(features[:3])}")
        
        return ". ".join(explanation_parts) + "."
    
    def _generate_cpt_explanation(
        self, 
        code: str, 
        clinical_text: str, 
        code_data: Dict
    ) -> str:
        """Generate human-readable explanation for CPT recommendation."""
        description = self.cpt_service.get_code_description(code)
        
        explanation_parts = [
            f"Recommended CPT code {code}: {description}",
            f"Confidence: {code_data['confidence']:.2%}",
            f"Source: {code_data['source']}"
        ]
        
        return ". ".join(explanation_parts) + "."
    
    def _generate_drg_explanation(
        self, 
        drg_code: str, 
        primary_icd10: str, 
        all_codes: List[str]
    ) -> str:
        """Generate human-readable explanation for DRG recommendation."""
        description = self.drg_service.get_drg_description(drg_code)
        
        explanation = (
            f"Recommended DRG {drg_code}: {description}. "
            f"Based on primary diagnosis {primary_icd10}"
        )
        
        if len(all_codes) > 1:
            explanation += f" and {len(all_codes) - 1} secondary diagnoses"
        
        return explanation + "."
    
    def _generate_summary(self, recommendations: List[CodeRecommendationResponse]) -> Dict[str, Any]:
        """Generate summary statistics for recommendations."""
        if not recommendations:
            return {"total_recommendations": 0}
        
        by_type = {}
        confidence_scores = []
        
        for rec in recommendations:
            by_type[rec.code_type] = by_type.get(rec.code_type, 0) + 1
            confidence_scores.append(rec.confidence_score)
        
        return {
            "total_recommendations": len(recommendations),
            "by_type": by_type,
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores),
            "high_confidence_count": len([c for c in confidence_scores if c >= 0.8])
        }
