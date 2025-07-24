"""
Audit Service for FairClaimRCM

Provides comprehensive audit logging and tracking capabilities.
"""

from typing import Dict, Any, Optional
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
