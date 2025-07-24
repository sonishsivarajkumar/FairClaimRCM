"""
Coding Service for FairClaimRCM v0.2

Enhanced medical coding recommendations with ML-powered intelligence,
sophisticated confidence scoring, and batch processing capabilities.
"""

import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

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
    Enhanced coding service with ML-powered intelligence and batch processing.
    
    Combines sophisticated rule-based and ML approaches to suggest appropriate
    ICD-10, CPT, and DRG codes with detailed confidence scoring and audit capabilities.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.icd10_service = ICD10Service()
        self.cpt_service = CPTService()
        self.drg_service = DRGService()
        self.code_predictor = CodePredictor()
        self.audit_service = AuditService(db)
        self.version = "v0.2.0"
    
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
                model_version=self.version
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
    
    async def generate_recommendations_batch(
        self,
        batch_requests: List[Dict[str, Any]],
        include_explanations: bool = True,
        enable_parallel_processing: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate coding recommendations for multiple claims in batch.
        
        Args:
            batch_requests: List of batch request dictionaries with claim_id and clinical_text
            include_explanations: Whether to include detailed reasoning
            enable_parallel_processing: Enable parallel processing for better performance
            
        Returns:
            List of batch results with recommendations and processing metadata
        """
        batch_id = str(uuid.uuid4())
        batch_start_time = datetime.utcnow()
        
        # Log batch processing start
        await self.audit_service.log_action(
            claim_id=f"batch_{batch_id}",
            action="batch_coding_started",
            details={
                "batch_size": len(batch_requests),
                "batch_id": batch_id,
                "parallel_processing": enable_parallel_processing
            },
            user_id="system"
        )
        
        batch_results = []
        
        try:
            if enable_parallel_processing and len(batch_requests) > 1:
                # Extract clinical texts for batch ML processing
                clinical_texts = [req['clinical_text'] for req in batch_requests]
                ml_batch_results = await self.code_predictor.predict_codes_batch(
                    clinical_texts, include_confidence_analysis=True
                )
                
                # Process each request with ML results
                for i, request in enumerate(batch_requests):
                    ml_result = ml_batch_results[i] if i < len(ml_batch_results) else None
                    result = await self._process_single_batch_request(
                        request, include_explanations, ml_result, batch_id
                    )
                    batch_results.append(result)
            else:
                # Sequential processing
                for i, request in enumerate(batch_requests):
                    result = await self._process_single_batch_request(
                        request, include_explanations, None, batch_id
                    )
                    batch_results.append(result)
        
        except Exception as e:
            # Log batch processing error
            await self.audit_service.log_action(
                claim_id=f"batch_{batch_id}",
                action="batch_coding_error",
                details={
                    "error": str(e),
                    "batch_id": batch_id,
                    "processed_count": len(batch_results)
                },
                user_id="system"
            )
            raise
        
        # Calculate batch processing statistics
        batch_end_time = datetime.utcnow()
        processing_duration = (batch_end_time - batch_start_time).total_seconds()
        
        batch_summary = self._generate_batch_summary(batch_results, processing_duration)
        
        # Log batch completion
        await self.audit_service.log_action(
            claim_id=f"batch_{batch_id}",
            action="batch_coding_completed",
            details={
                "batch_id": batch_id,
                "processing_duration_seconds": processing_duration,
                "summary": batch_summary
            },
            user_id="system"
        )
        
        return {
            "batch_id": batch_id,
            "processing_duration_seconds": processing_duration,
            "results": batch_results,
            "summary": batch_summary
        }
    
    async def _process_single_batch_request(
        self,
        request: Dict[str, Any],
        include_explanations: bool,
        ml_result: Optional[Dict] = None,
        batch_id: str = ""
    ) -> Dict[str, Any]:
        """
        Process a single request within a batch operation.
        """
        try:
            claim_id = request.get('claim_id', f"batch_item_{uuid.uuid4()}")
            clinical_text = request.get('clinical_text', '')
            
            if ml_result and 'error' not in ml_result:
                # Use pre-computed ML results for efficiency
                recommendations = await self._generate_recommendations_from_ml_batch(
                    claim_id, clinical_text, ml_result, include_explanations
                )
            else:
                # Fallback to individual processing
                coding_response = await self.generate_recommendations(
                    claim_id, clinical_text, include_explanations
                )
                recommendations = coding_response.recommendations
            
            return {
                "claim_id": claim_id,
                "status": "success",
                "recommendations": [rec.dict() for rec in recommendations],
                "batch_id": batch_id,
                "processing_method": "ml_batch" if ml_result else "individual"
            }
            
        except Exception as e:
            return {
                "claim_id": request.get('claim_id', 'unknown'),
                "status": "error",
                "error": str(e),
                "batch_id": batch_id
            }
    
    async def _generate_recommendations_from_ml_batch(
        self,
        claim_id: str,
        clinical_text: str,
        ml_result: Dict,
        include_explanations: bool
    ) -> List[CodeRecommendationResponse]:
        """
        Generate recommendations using pre-computed ML batch results.
        """
        recommendations = []
        
        # Process ICD-10 predictions
        if 'icd10_predictions' in ml_result:
            for pred in ml_result['icd10_predictions']:
                explanation = ""
                if include_explanations:
                    explanation = self._generate_enhanced_explanation(pred, 'ICD10')
                
                recommendations.append(CodeRecommendationResponse(
                    code=pred['code'],
                    code_type=CodeType.ICD10,
                    confidence_score=pred['confidence'],
                    reasoning=explanation,
                    recommendation_source=RecommendationSource.ML_MODEL
                ))
        
        # Process CPT predictions
        if 'cpt_predictions' in ml_result:
            for pred in ml_result['cpt_predictions']:
                explanation = ""
                if include_explanations:
                    explanation = self._generate_enhanced_explanation(pred, 'CPT')
                
                recommendations.append(CodeRecommendationResponse(
                    code=pred['code'],
                    code_type=CodeType.CPT,
                    confidence_score=pred['confidence'],
                    reasoning=explanation,
                    recommendation_source=RecommendationSource.ML_MODEL
                ))
        
        # Generate DRG recommendations if ICD-10 codes exist
        icd10_codes = [rec.code for rec in recommendations if rec.code_type == CodeType.ICD10]
        if icd10_codes:
            primary_icd10 = icd10_codes[0]
            drg_recs = await self._generate_drg_recommendations(
                primary_icd10, icd10_codes, include_explanations
            )
            recommendations.extend(drg_recs)
        
        # Save recommendations to database
        await self._save_recommendations_batch(claim_id, recommendations)
        
        return recommendations
    
    async def _save_recommendations_batch(
        self, 
        claim_id: str, 
        recommendations: List[CodeRecommendationResponse]
    ) -> None:
        """
        Efficiently save batch recommendations to database.
        """
        db_recommendations = []
        for rec in recommendations:
            db_rec = CodeRecommendationModel(
                claim_id=claim_id,
                code=rec.code,
                code_type=rec.code_type,
                confidence_score=rec.confidence_score,
                reasoning=rec.reasoning,
                recommendation_source=rec.recommendation_source,
                model_version=self.version
            )
            db_recommendations.append(db_rec)
        
        self.db.add_all(db_recommendations)
        self.db.commit()
    
    def _generate_enhanced_explanation(self, prediction: Dict, code_type: str) -> str:
        """
        Generate enhanced explanations using ML prediction details.
        """
        explanation_parts = [
            f"ML-powered {code_type} recommendation: {prediction['code']}",
            f"Confidence: {prediction['confidence']:.1%}"
        ]
        
        if 'confidence_breakdown' in prediction:
            breakdown = prediction['confidence_breakdown']
            explanation_parts.append(
                f"Based on pattern analysis (base: {breakdown.get('base_score', 0):.2f}, "
                f"context: {breakdown.get('context_boost', 0):.2f})"
            )
        
        if 'features' in prediction and prediction['features']:
            explanation_parts.append(
                f"Key indicators: {', '.join(prediction['features'][:3])}"
            )
        
        if 'reasoning_factors' in prediction and prediction['reasoning_factors']:
            top_factors = prediction['reasoning_factors'][:2]
            explanation_parts.append(f"Reasoning: {'; '.join(top_factors)}")
        
        return ". ".join(explanation_parts) + "."
    
    def _generate_batch_summary(
        self, 
        batch_results: List[Dict], 
        processing_duration: float
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary for batch processing results.
        """
        successful_results = [r for r in batch_results if r.get('status') == 'success']
        failed_results = [r for r in batch_results if r.get('status') == 'error']
        
        total_recommendations = sum(
            len(r.get('recommendations', [])) for r in successful_results
        )
        
        # Analyze confidence distributions
        all_confidences = []
        code_type_counts = {'ICD10': 0, 'CPT': 0, 'DRG': 0}
        
        for result in successful_results:
            for rec in result.get('recommendations', []):
                all_confidences.append(rec.get('confidence_score', 0))
                code_type = rec.get('code_type', 'Unknown')
                if code_type in code_type_counts:
                    code_type_counts[code_type] += 1
        
        confidence_stats = {}
        if all_confidences:
            confidence_stats = {
                'average': sum(all_confidences) / len(all_confidences),
                'min': min(all_confidences),
                'max': max(all_confidences),
                'high_confidence_count': len([c for c in all_confidences if c >= 0.8])
            }
        
        return {
            'total_requests': len(batch_results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'total_recommendations': total_recommendations,
            'processing_duration_seconds': processing_duration,
            'average_processing_time_per_request': processing_duration / len(batch_results) if batch_results else 0,
            'code_type_distribution': code_type_counts,
            'confidence_statistics': confidence_stats,
            'throughput_requests_per_second': len(batch_results) / processing_duration if processing_duration > 0 else 0
        }
    
    async def get_confidence_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        code_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed confidence analytics for recommendations.
        
        Args:
            start_date: Start of analysis period
            end_date: End of analysis period
            code_type: Optional filter by code type (ICD10, CPT, DRG)
            
        Returns:
            Comprehensive confidence analytics
        """
        # Query recommendations in date range
        query = self.db.query(CodeRecommendationModel).filter(
            CodeRecommendationModel.created_at >= start_date,
            CodeRecommendationModel.created_at <= end_date
        )
        
        if code_type:
            query = query.filter(CodeRecommendationModel.code_type == code_type)
        
        recommendations = query.all()
        
        if not recommendations:
            return {
                "status": "no_data",
                "message": "No recommendations found in specified date range"
            }
        
        # Extract confidence scores and metadata
        confidence_scores = [rec.confidence_score for rec in recommendations]
        
        # Calculate statistics
        analytics = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_recommendations": len(recommendations)
            },
            "confidence_statistics": {
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "min_confidence": min(confidence_scores),
                "max_confidence": max(confidence_scores),
                "median_confidence": sorted(confidence_scores)[len(confidence_scores) // 2],
                "std_deviation": self._calculate_std_dev(confidence_scores)
            },
            "confidence_distribution": {
                "excellent": len([c for c in confidence_scores if c >= 0.9]),
                "good": len([c for c in confidence_scores if 0.7 <= c < 0.9]),
                "fair": len([c for c in confidence_scores if 0.5 <= c < 0.7]),
                "poor": len([c for c in confidence_scores if c < 0.5])
            },
            "performance_by_code_type": self._analyze_performance_by_type(recommendations),
            "performance_by_source": self._analyze_performance_by_source(recommendations),
            "temporal_trends": self._analyze_temporal_trends(recommendations),
            "quality_indicators": self._calculate_quality_indicators(recommendations)
        }
        
        return analytics
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _analyze_performance_by_type(self, recommendations: List) -> Dict[str, Any]:
        """Analyze performance metrics by code type."""
        by_type = {}
        
        for code_type in ['ICD10', 'CPT', 'DRG']:
            type_recs = [r for r in recommendations if r.code_type == code_type]
            if type_recs:
                confidences = [r.confidence_score for r in type_recs]
                by_type[code_type] = {
                    "count": len(type_recs),
                    "average_confidence": sum(confidences) / len(confidences),
                    "high_confidence_rate": len([c for c in confidences if c >= 0.8]) / len(confidences),
                    "approval_rate": len([r for r in type_recs if r.approved]) / len(type_recs)
                }
        
        return by_type
    
    def _analyze_performance_by_source(self, recommendations: List) -> Dict[str, Any]:
        """Analyze performance metrics by recommendation source."""
        by_source = {}
        
        for source in ['rule_based', 'ml_model', 'hybrid']:
            source_recs = [r for r in recommendations if r.recommendation_source == source]
            if source_recs:
                confidences = [r.confidence_score for r in source_recs]
                by_source[source] = {
                    "count": len(source_recs),
                    "average_confidence": sum(confidences) / len(confidences),
                    "high_confidence_rate": len([c for c in confidences if c >= 0.8]) / len(confidences),
                    "approval_rate": len([r for r in source_recs if r.approved]) / len(source_recs)
                }
        
        return by_source
    
    def _analyze_temporal_trends(self, recommendations: List) -> Dict[str, Any]:
        """Analyze confidence trends over time."""
        from collections import defaultdict
        
        daily_stats = defaultdict(list)
        
        for rec in recommendations:
            day = rec.created_at.date().isoformat()
            daily_stats[day].append(rec.confidence_score)
        
        trends = {}
        for day, confidences in daily_stats.items():
            trends[day] = {
                "average_confidence": sum(confidences) / len(confidences),
                "recommendation_count": len(confidences),
                "high_confidence_count": len([c for c in confidences if c >= 0.8])
            }
        
        return trends
    
    def _calculate_quality_indicators(self, recommendations: List) -> Dict[str, Any]:
        """Calculate overall quality indicators."""
        if not recommendations:
            return {}
        
        confidences = [r.confidence_score for r in recommendations]
        total_recs = len(recommendations)
        
        return {
            "overall_quality_score": sum(confidences) / total_recs,
            "consistency_score": 1.0 - (self._calculate_std_dev(confidences) / max(confidences)) if max(confidences) > 0 else 0,
            "reliability_indicators": {
                "high_confidence_percentage": len([c for c in confidences if c >= 0.8]) / total_recs * 100,
                "low_confidence_percentage": len([c for c in confidences if c < 0.5]) / total_recs * 100,
                "approved_percentage": len([r for r in recommendations if r.approved]) / total_recs * 100
            },
            "ml_effectiveness": {
                "ml_recommendations": len([r for r in recommendations if r.recommendation_source == 'ml_model']),
                "ml_average_confidence": sum([r.confidence_score for r in recommendations if r.recommendation_source == 'ml_model']) / 
                                       len([r for r in recommendations if r.recommendation_source == 'ml_model']) 
                                       if [r for r in recommendations if r.recommendation_source == 'ml_model'] else 0
            }
        }
    
    async def get_recommendations_by_claim(
        self,
        claim_id: str,
        include_audit: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve all recommendations for a specific claim.
        
        Args:
            claim_id: The claim identifier
            include_audit: Whether to include audit information
            
        Returns:
            Dictionary with recommendations and optional audit data
        """
        recommendations = self.db.query(CodeRecommendationModel).filter(
            CodeRecommendationModel.claim_id == claim_id
        ).order_by(CodeRecommendationModel.confidence_score.desc()).all()
        
        if not recommendations:
            return {
                "claim_id": claim_id,
                "recommendations": [],
                "summary": {"total_recommendations": 0}
            }
        
        # Convert to response format
        rec_responses = []
        for rec in recommendations:
            rec_responses.append(CodeRecommendationResponse(
                code=rec.code,
                code_type=rec.code_type,
                confidence_score=rec.confidence_score,
                reasoning=rec.reasoning,
                recommendation_source=rec.recommendation_source
            ))
        
        result = {
            "claim_id": claim_id,
            "recommendations": rec_responses,
            "summary": self._generate_summary(rec_responses)
        }
        
        if include_audit:
            audit_logs = self.db.query(AuditLog).filter(
                AuditLog.claim_id == claim_id
            ).order_by(AuditLog.timestamp.desc()).all()
            
            result["audit_history"] = [
                {
                    "action": log.action,
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": log.user_id,
                    "details": log.details
                }
                for log in audit_logs
            ]
        
        return result
    
    async def approve_recommendation(
        self,
        recommendation_id: int,
        user_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve a specific code recommendation.
        
        Args:
            recommendation_id: The recommendation ID to approve
            user_id: The user approving the recommendation
            notes: Optional approval notes
            
        Returns:
            Approval result with updated recommendation data
        """
        recommendation = self.db.query(CodeRecommendationModel).filter(
            CodeRecommendationModel.id == recommendation_id
        ).first()
        
        if not recommendation:
            return {
                "status": "error",
                "message": f"Recommendation {recommendation_id} not found"
            }
        
        if recommendation.approved:
            return {
                "status": "warning",
                "message": "Recommendation already approved",
                "recommendation": recommendation
            }
        
        # Update recommendation
        recommendation.approved = True
        recommendation.reviewed_by = user_id
        self.db.commit()
        
        # Create audit log
        audit_details = {
            "recommendation_id": recommendation_id,
            "code": recommendation.code,
            "code_type": recommendation.code_type,
            "confidence_score": recommendation.confidence_score
        }
        
        if notes:
            audit_details["approval_notes"] = notes
        
        await self.audit_service.log_action(
            claim_id=recommendation.claim_id,
            action="recommendation_approved",
            details=audit_details,
            user_id=user_id
        )
        
        return {
            "status": "success",
            "message": "Recommendation approved successfully",
            "recommendation_id": recommendation_id,
            "claim_id": recommendation.claim_id,
            "approved_by": user_id,
            "approval_timestamp": datetime.utcnow().isoformat()
        }
    
    async def bulk_approve_recommendations(
        self,
        recommendation_ids: List[int],
        user_id: str,
        approval_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Approve multiple recommendations in bulk.
        
        Args:
            recommendation_ids: List of recommendation IDs to approve
            user_id: The user approving recommendations
            approval_criteria: Optional criteria used for bulk approval
            
        Returns:
            Bulk approval results with success/failure counts
        """
        approved_count = 0
        failed_approvals = []
        
        for rec_id in recommendation_ids:
            try:
                result = await self.approve_recommendation(rec_id, user_id)
                if result["status"] == "success":
                    approved_count += 1
                else:
                    failed_approvals.append({
                        "recommendation_id": rec_id,
                        "error": result["message"]
                    })
            except Exception as e:
                failed_approvals.append({
                    "recommendation_id": rec_id,
                    "error": str(e)
                })
        
        # Log bulk approval action
        await self.audit_service.log_action(
            claim_id="bulk_operation",
            action="bulk_recommendations_approved",
            details={
                "total_requested": len(recommendation_ids),
                "approved_count": approved_count,
                "failed_count": len(failed_approvals),
                "approval_criteria": approval_criteria,
                "failed_approvals": failed_approvals
            },
            user_id=user_id
        )
        
        return {
            "status": "completed",
            "total_requested": len(recommendation_ids),
            "approved_count": approved_count,
            "failed_count": len(failed_approvals),
            "failed_approvals": failed_approvals,
            "success_rate": approved_count / len(recommendation_ids) * 100 if recommendation_ids else 0
        }
    
    async def get_code_performance_metrics(
        self,
        code: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a specific code.
        
        Args:
            code: The medical code to analyze
            start_date: Optional start date for analysis
            end_date: Optional end date for analysis
            
        Returns:
            Comprehensive performance metrics for the code
        """
        query = self.db.query(CodeRecommendationModel).filter(
            CodeRecommendationModel.code == code
        )
        
        if start_date:
            query = query.filter(CodeRecommendationModel.created_at >= start_date)
        if end_date:
            query = query.filter(CodeRecommendationModel.created_at <= end_date)
        
        recommendations = query.all()
        
        if not recommendations:
            return {
                "code": code,
                "status": "no_data",
                "message": "No recommendations found for this code"
            }
        
        # Calculate metrics
        total_recommendations = len(recommendations)
        approved_recs = [r for r in recommendations if r.approved]
        confidence_scores = [r.confidence_score for r in recommendations]
        
        # Performance by source
        by_source = {}
        for source in ['rule_based', 'ml_model', 'hybrid']:
            source_recs = [r for r in recommendations if r.recommendation_source == source]
            if source_recs:
                by_source[source] = {
                    "count": len(source_recs),
                    "approval_rate": len([r for r in source_recs if r.approved]) / len(source_recs),
                    "average_confidence": sum([r.confidence_score for r in source_recs]) / len(source_recs)
                }
        
        # Temporal analysis
        monthly_stats = {}
        for rec in recommendations:
            month_key = rec.created_at.strftime("%Y-%m")
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    "recommendations": 0,
                    "approvals": 0,
                    "total_confidence": 0
                }
            
            monthly_stats[month_key]["recommendations"] += 1
            monthly_stats[month_key]["total_confidence"] += rec.confidence_score
            if rec.approved:
                monthly_stats[month_key]["approvals"] += 1
        
        # Calculate monthly averages
        for month_data in monthly_stats.values():
            month_data["approval_rate"] = month_data["approvals"] / month_data["recommendations"]
            month_data["average_confidence"] = month_data["total_confidence"] / month_data["recommendations"]
        
        return {
            "code": code,
            "analysis_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "total_recommendations": total_recommendations
            },
            "overall_performance": {
                "approval_rate": len(approved_recs) / total_recommendations,
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "confidence_std_dev": self._calculate_std_dev(confidence_scores),
                "high_confidence_rate": len([c for c in confidence_scores if c >= 0.8]) / len(confidence_scores)
            },
            "performance_by_source": by_source,
            "temporal_trends": monthly_stats,
            "quality_indicators": {
                "consistency_score": 1.0 - (self._calculate_std_dev(confidence_scores) / max(confidence_scores)) if max(confidence_scores) > 0 else 0,
                "reliability_score": len(approved_recs) / total_recommendations
            }
        }
    
    async def validate_recommendations(
        self,
        claim_id: str,
        validation_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate recommendations against business rules and guidelines.
        
        Args:
            claim_id: The claim ID to validate
            validation_rules: Optional custom validation rules
            
        Returns:
            Validation results with any issues found
        """
        recommendations = self.db.query(CodeRecommendationModel).filter(
            CodeRecommendationModel.claim_id == claim_id
        ).all()
        
        if not recommendations:
            return {
                "claim_id": claim_id,
                "status": "no_recommendations",
                "message": "No recommendations found for validation"
            }
        
        validation_results = {
            "claim_id": claim_id,
            "total_recommendations": len(recommendations),
            "validation_passed": True,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Default validation rules
        default_rules = {
            "min_confidence_threshold": 0.3,
            "max_recommendations_per_type": {"ICD10": 10, "CPT": 5, "DRG": 2},
            "require_primary_diagnosis": True,
            "confidence_consistency_threshold": 0.2
        }
        
        # Merge with custom rules
        rules = {**default_rules, **(validation_rules or {})}
        
        # Count by type
        by_type = {}
        confidence_scores = []
        
        for rec in recommendations:
            by_type[rec.code_type] = by_type.get(rec.code_type, 0) + 1
            confidence_scores.append(rec.confidence_score)
            
            # Check minimum confidence
            if rec.confidence_score < rules["min_confidence_threshold"]:
                validation_results["issues"].append({
                    "type": "low_confidence",
                    "code": rec.code,
                    "confidence": rec.confidence_score,
                    "threshold": rules["min_confidence_threshold"],
                    "message": f"Code {rec.code} has confidence below threshold"
                })
                validation_results["validation_passed"] = False
        
        # Check max recommendations per type
        for code_type, count in by_type.items():
            max_allowed = rules["max_recommendations_per_type"].get(code_type, 999)
            if count > max_allowed:
                validation_results["warnings"].append({
                    "type": "excessive_recommendations",
                    "code_type": code_type,
                    "count": count,
                    "max_allowed": max_allowed,
                    "message": f"Too many {code_type} recommendations ({count} > {max_allowed})"
                })
        
        # Check for primary diagnosis
        if rules["require_primary_diagnosis"] and "ICD10" not in by_type:
            validation_results["issues"].append({
                "type": "missing_primary_diagnosis",
                "message": "No ICD10 diagnosis codes found"
            })
            validation_results["validation_passed"] = False
        
        # Check confidence consistency
        if len(confidence_scores) > 1:
            confidence_std = self._calculate_std_dev(confidence_scores)
            confidence_mean = sum(confidence_scores) / len(confidence_scores)
            if confidence_std / confidence_mean > rules["confidence_consistency_threshold"]:
                validation_results["warnings"].append({
                    "type": "confidence_inconsistency",
                    "std_deviation": confidence_std,
                    "mean": confidence_mean,
                    "coefficient_variation": confidence_std / confidence_mean,
                    "message": "High variability in confidence scores detected"
                })
        
        # Generate suggestions based on validation results
        if validation_results["issues"] or validation_results["warnings"]:
            if any(issue["type"] == "low_confidence" for issue in validation_results["issues"]):
                validation_results["suggestions"].append(
                    "Consider reviewing clinical text quality or updating ML models for low-confidence recommendations"
                )
            
            if any(warning["type"] == "excessive_recommendations" for warning in validation_results["warnings"]):
                validation_results["suggestions"].append(
                    "Review recommendation algorithms to reduce noise and improve precision"
                )
        
        return validation_results
