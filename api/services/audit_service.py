"""
Audit Service for FairClaimRCM

Provides comprehensive audit logging and tracking capabilities.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from api.models.database import AuditLog as AuditLogModel

class AuditService:
    """
    Service for managing audit logs and compliance tracking.
    
    Ensures all actions are properly logged for transparency and compliance
    with healthcare regulations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_action(
        self,
        claim_id: str,
        action: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditLogModel:
        """
        Log an action for audit trail purposes.
        
        Args:
            claim_id: Unique claim identifier
            action: Description of the action performed
            details: Additional details about the action
            user_id: ID of the user who performed the action
            
        Returns:
            Created audit log entry
        """
        audit_log = AuditLogModel(
            claim_id=claim_id,
            action=action,
            details=details,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    async def get_claim_audit_trail(self, claim_id: str) -> list:
        """
        Retrieve complete audit trail for a claim.
        
        Args:
            claim_id: Unique claim identifier
            
        Returns:
            List of audit log entries for the claim
        """
        return self.db.query(AuditLogModel).filter(
            AuditLogModel.claim_id == claim_id
        ).order_by(AuditLogModel.timestamp.desc()).all()
    
    async def get_user_actions(self, user_id: str, limit: int = 100) -> list:
        """
        Retrieve recent actions by a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries for the user
        """
        return self.db.query(AuditLogModel).filter(
            AuditLogModel.user_id == user_id
        ).order_by(AuditLogModel.timestamp.desc()).limit(limit).all()
    
    async def generate_compliance_report(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate a compliance report for a given time period.
        
        Args:
            start_date: Start of reporting period
            end_date: End of reporting period
            
        Returns:
            Compliance report with statistics and summaries
        """
        logs = self.db.query(AuditLogModel).filter(
            AuditLogModel.timestamp >= start_date,
            AuditLogModel.timestamp <= end_date
        ).all()
        
        # Calculate statistics
        total_actions = len(logs)
        unique_claims = len(set(log.claim_id for log in logs))
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        
        # Action breakdown
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        # Daily activity
        daily_activity = {}
        for log in logs:
            date_key = log.timestamp.date().isoformat()
            daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "statistics": {
                "total_actions": total_actions,
                "unique_claims": unique_claims,
                "unique_users": unique_users,
                "actions_per_claim": total_actions / unique_claims if unique_claims > 0 else 0
            },
            "action_breakdown": action_counts,
            "daily_activity": daily_activity
        }
    
    async def generate_detailed_audit_report(
        self, 
        start_date: datetime, 
        end_date: datetime,
        include_ml_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Generate detailed audit report with ML performance metrics.
        
        Args:
            start_date: Start of reporting period
            end_date: End of reporting period
            include_ml_metrics: Include ML model performance analysis
            
        Returns:
            Comprehensive audit report with detailed analytics
        """
        # Get all audit logs in date range
        audit_logs = self.db.query(AuditLogModel).filter(
            AuditLogModel.timestamp >= start_date,
            AuditLogModel.timestamp <= end_date
        ).all()
        
        report = {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': (end_date - start_date).days
            },
            'summary_statistics': self._calculate_audit_summary(audit_logs),
            'activity_analysis': self._analyze_audit_activities(audit_logs),
            'performance_metrics': self._calculate_performance_metrics(audit_logs),
            'compliance_indicators': self._assess_compliance_indicators(audit_logs)
        }
        
        if include_ml_metrics:
            report['ml_performance'] = await self._analyze_ml_performance(audit_logs)
        
        return report
    
    def _calculate_audit_summary(self, audit_logs: list) -> Dict[str, Any]:
        """Calculate summary statistics for audit logs."""
        total_actions = len(audit_logs)
        unique_claims = len(set(log.claim_id for log in audit_logs))
        unique_users = len(set(log.user_id for log in audit_logs if log.user_id))
        
        action_types = {}
        for log in audit_logs:
            action_types[log.action] = action_types.get(log.action, 0) + 1
        
        return {
            'total_actions': total_actions,
            'unique_claims_processed': unique_claims,
            'unique_users_active': unique_users,
            'most_common_actions': sorted(
                action_types.items(), key=lambda x: x[1], reverse=True
            )[:5],
            'daily_average_actions': total_actions / max(1, (
                max([log.timestamp for log in audit_logs]) - 
                min([log.timestamp for log in audit_logs])
            ).days) if audit_logs else 0
        }
    
    def _analyze_audit_activities(self, audit_logs: list) -> Dict[str, Any]:
        """Analyze patterns in audit activities."""
        coding_actions = [
            log for log in audit_logs 
            if 'coding' in log.action.lower()
        ]
        
        batch_actions = [
            log for log in audit_logs 
            if 'batch' in log.action.lower()
        ]
        
        error_actions = [
            log for log in audit_logs 
            if 'error' in log.action.lower()
        ]
        
        return {
            'coding_activities': {
                'total_coding_actions': len(coding_actions),
                'percentage_of_total': len(coding_actions) / len(audit_logs) * 100 if audit_logs else 0
            },
            'batch_processing': {
                'batch_operations': len(batch_actions),
                'average_batch_size': self._calculate_average_batch_size(batch_actions)
            },
            'error_analysis': {
                'total_errors': len(error_actions),
                'error_rate': len(error_actions) / len(audit_logs) * 100 if audit_logs else 0,
                'common_error_types': self._analyze_common_errors(error_actions)
            }
        }
    
    def _calculate_performance_metrics(self, audit_logs: list) -> Dict[str, Any]:
        """Calculate performance metrics from audit data."""
        processing_times = []
        recommendation_counts = []
        confidence_scores = []
        
        for log in audit_logs:
            details = log.details
            if isinstance(details, dict):
                # Extract processing duration if available
                if 'processing_duration_seconds' in details:
                    processing_times.append(details['processing_duration_seconds'])
                
                # Extract recommendation counts
                if 'num_recommendations' in details:
                    recommendation_counts.append(details['num_recommendations'])
                
                # Extract confidence scores
                if 'confidence_scores' in details:
                    confidence_scores.extend(details['confidence_scores'])
        
        metrics = {
            'processing_performance': {},
            'recommendation_quality': {},
            'system_efficiency': {}
        }
        
        if processing_times:
            metrics['processing_performance'] = {
                'average_processing_time': sum(processing_times) / len(processing_times),
                'min_processing_time': min(processing_times),
                'max_processing_time': max(processing_times),
                'processing_samples': len(processing_times)
            }
        
        if recommendation_counts:
            metrics['recommendation_quality'] = {
                'average_recommendations_per_claim': sum(recommendation_counts) / len(recommendation_counts),
                'total_recommendations_generated': sum(recommendation_counts)
            }
        
        if confidence_scores:
            metrics['system_efficiency'] = {
                'average_confidence': sum(confidence_scores) / len(confidence_scores),
                'high_confidence_percentage': len([c for c in confidence_scores if c >= 0.8]) / len(confidence_scores) * 100
            }
        
        return metrics
    
    def _assess_compliance_indicators(self, audit_logs: list) -> Dict[str, Any]:
        """Assess compliance-related indicators."""
        return {
            'audit_trail_completeness': {
                'total_logged_actions': len(audit_logs),
                'actions_with_user_id': len([log for log in audit_logs if log.user_id]),
                'actions_with_details': len([log for log in audit_logs if log.details])
            },
            'data_integrity': {
                'claims_with_complete_trail': self._count_complete_trails(audit_logs),
                'average_actions_per_claim': len(audit_logs) / len(set(log.claim_id for log in audit_logs)) if audit_logs else 0
            },
            'system_reliability': {
                'successful_operations': len([log for log in audit_logs if 'error' not in log.action.lower()]),
                'reliability_percentage': len([log for log in audit_logs if 'error' not in log.action.lower()]) / len(audit_logs) * 100 if audit_logs else 100
            }
        }
    
    async def _analyze_ml_performance(self, audit_logs: list) -> Dict[str, Any]:
        """Analyze ML model performance from audit data."""
        ml_actions = [
            log for log in audit_logs 
            if log.details and isinstance(log.details, dict) and 
            any(key in log.details for key in ['confidence_scores', 'recommendation_types'])
        ]
        
        if not ml_actions:
            return {'status': 'no_ml_data_available'}
        
        confidence_scores = []
        code_type_distribution = {'ICD10': 0, 'CPT': 0, 'DRG': 0}
        
        for log in ml_actions:
            details = log.details
            if 'confidence_scores' in details:
                confidence_scores.extend(details['confidence_scores'])
            
            if 'recommendation_types' in details:
                for code_type in details['recommendation_types']:
                    if code_type in code_type_distribution:
                        code_type_distribution[code_type] += 1
        
        performance_analysis = {
            'confidence_analysis': {},
            'prediction_distribution': code_type_distribution,
            'model_consistency': {},
            'recommendation_patterns': {}
        }
        
        if confidence_scores:
            performance_analysis['confidence_analysis'] = {
                'average_confidence': sum(confidence_scores) / len(confidence_scores),
                'confidence_std_dev': self._calculate_std_dev(confidence_scores),
                'high_confidence_rate': len([c for c in confidence_scores if c >= 0.8]) / len(confidence_scores),
                'low_confidence_rate': len([c for c in confidence_scores if c < 0.5]) / len(confidence_scores),
                'confidence_distribution': {
                    'excellent': len([c for c in confidence_scores if c >= 0.9]),
                    'good': len([c for c in confidence_scores if 0.7 <= c < 0.9]),
                    'fair': len([c for c in confidence_scores if 0.5 <= c < 0.7]),
                    'poor': len([c for c in confidence_scores if c < 0.5])
                }
            }
        
        return performance_analysis
    
    def _calculate_average_batch_size(self, batch_actions: list) -> float:
        """Calculate average batch size from batch audit logs."""
        batch_sizes = []
        for log in batch_actions:
            if log.details and isinstance(log.details, dict) and 'batch_size' in log.details:
                batch_sizes.append(log.details['batch_size'])
        
        return sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
    
    def _analyze_common_errors(self, error_actions: list) -> List[Dict[str, Any]]:
        """Analyze common error patterns."""
        error_patterns = {}
        for log in error_actions:
            if log.details and isinstance(log.details, dict) and 'error' in log.details:
                error_type = log.details['error'][:50]  # First 50 chars
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
        
        return [
            {'error_pattern': pattern, 'frequency': count}
            for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _count_complete_trails(self, audit_logs: list) -> int:
        """Count claims with complete audit trails."""
        claim_action_counts = {}
        for log in audit_logs:
            claim_action_counts[log.claim_id] = claim_action_counts.get(log.claim_id, 0) + 1
        
        # Consider a trail "complete" if it has at least 2 actions
        return len([claim for claim, count in claim_action_counts.items() if count >= 2])
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
