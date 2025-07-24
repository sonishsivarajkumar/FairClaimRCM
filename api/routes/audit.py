"""
Audit API routes for FairClaimRCM

Handles audit trail and compliance reporting operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from api.models.database import get_db
from api.models.schemas import AuditLog
from api.services.audit_service import AuditService

router = APIRouter()

@router.get("/logs/{claim_id}", response_model=List[AuditLog])
async def get_claim_audit_logs(
    claim_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete audit trail for a specific claim.
    
    Returns all logged actions and changes for the specified claim,
    providing full transparency and compliance tracking.
    """
    audit_service = AuditService(db)
    logs = await audit_service.get_claim_audit_trail(claim_id)
    
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audit logs found for claim {claim_id}"
        )
    
    return logs

@router.get("/user/{user_id}", response_model=List[AuditLog])
async def get_user_audit_logs(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    db: Session = Depends(get_db)
):
    """
    Get recent audit logs for a specific user.
    
    Shows all actions performed by the specified user across all claims.
    """
    audit_service = AuditService(db)
    logs = await audit_service.get_user_actions(user_id, limit)
    
    return logs

@router.get("/recent")
async def get_recent_audit_logs(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    action_filter: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    db: Session = Depends(get_db)
):
    """
    Get recent audit logs across all claims.
    
    Provides a real-time view of system activity and user actions.
    """
    from api.models.database import AuditLog as AuditLogModel
    
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Build query
    query = db.query(AuditLogModel).filter(
        AuditLogModel.timestamp >= cutoff_time
    )
    
    if action_filter:
        query = query.filter(AuditLogModel.action.contains(action_filter))
    
    logs = query.order_by(
        AuditLogModel.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "period_hours": hours,
        "action_filter": action_filter,
        "total_logs": len(logs),
        "logs": logs
    }

@router.get("/compliance/report")
async def generate_compliance_report(
    start_date: datetime = Query(..., description="Start date for report"),
    end_date: datetime = Query(..., description="End date for report"),
    db: Session = Depends(get_db)
):
    """
    Generate a compliance report for a specified time period.
    
    Provides detailed analytics and statistics for compliance auditing
    and regulatory reporting requirements.
    """
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report period cannot exceed 365 days"
        )
    
    audit_service = AuditService(db)
    report = await audit_service.generate_compliance_report(start_date, end_date)
    
    return report

@router.get("/actions/summary")
async def get_action_summary(
    days: int = Query(30, ge=1, le=90, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get summary of audit actions over a specified period.
    
    Provides high-level metrics and trends for system activity monitoring.
    """
    from api.models.database import AuditLog as AuditLogModel
    from sqlalchemy import func
    
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    # Get action counts
    action_counts = db.query(
        AuditLogModel.action,
        func.count(AuditLogModel.id).label('count')
    ).filter(
        AuditLogModel.timestamp >= cutoff_time
    ).group_by(AuditLogModel.action).order_by(
        func.count(AuditLogModel.id).desc()
    ).all()
    
    # Get daily activity
    daily_activity = db.query(
        func.date(AuditLogModel.timestamp).label('date'),
        func.count(AuditLogModel.id).label('count')
    ).filter(
        AuditLogModel.timestamp >= cutoff_time
    ).group_by(
        func.date(AuditLogModel.timestamp)
    ).order_by('date').all()
    
    # Get user activity
    user_activity = db.query(
        AuditLogModel.user_id,
        func.count(AuditLogModel.id).label('count')
    ).filter(
        AuditLogModel.timestamp >= cutoff_time,
        AuditLogModel.user_id.isnot(None)
    ).group_by(AuditLogModel.user_id).order_by(
        func.count(AuditLogModel.id).desc()
    ).limit(10).all()
    
    # Get total statistics
    total_actions = db.query(func.count(AuditLogModel.id)).filter(
        AuditLogModel.timestamp >= cutoff_time
    ).scalar()
    
    unique_claims = db.query(func.count(func.distinct(AuditLogModel.claim_id))).filter(
        AuditLogModel.timestamp >= cutoff_time
    ).scalar()
    
    unique_users = db.query(func.count(func.distinct(AuditLogModel.user_id))).filter(
        AuditLogModel.timestamp >= cutoff_time,
        AuditLogModel.user_id.isnot(None)
    ).scalar()
    
    return {
        "period_days": days,
        "summary": {
            "total_actions": total_actions,
            "unique_claims": unique_claims,
            "unique_users": unique_users,
            "actions_per_day": total_actions / days if days > 0 else 0
        },
        "action_breakdown": [{"action": action, "count": count} for action, count in action_counts],
        "daily_activity": [{"date": str(date), "count": count} for date, count in daily_activity],
        "top_users": [{"user_id": user_id, "action_count": count} for user_id, count in user_activity]
    }

@router.get("/search")
async def search_audit_logs(
    query: str = Query(..., description="Search term"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    claim_id: Optional[str] = Query(None, description="Filter by claim ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search audit logs with various filters.
    
    Provides flexible search capabilities for audit log analysis and investigation.
    """
    from api.models.database import AuditLog as AuditLogModel
    
    # Build base query
    query_obj = db.query(AuditLogModel)
    
    # Apply search term to action and details
    if query:
        query_obj = query_obj.filter(
            AuditLogModel.action.contains(query) |
            AuditLogModel.details.astext.contains(query)
        )
    
    # Apply date filters
    if start_date:
        query_obj = query_obj.filter(AuditLogModel.timestamp >= start_date)
    
    if end_date:
        query_obj = query_obj.filter(AuditLogModel.timestamp <= end_date)
    
    # Apply ID filters
    if claim_id:
        query_obj = query_obj.filter(AuditLogModel.claim_id == claim_id)
    
    if user_id:
        query_obj = query_obj.filter(AuditLogModel.user_id == user_id)
    
    # Get total count
    total_count = query_obj.count()
    
    # Apply limit and get results
    results = query_obj.order_by(
        AuditLogModel.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "search_query": query,
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "claim_id": claim_id,
            "user_id": user_id
        },
        "total_results": total_count,
        "returned_results": len(results),
        "logs": results
    }

@router.get("/export/csv")
async def export_audit_logs_csv(
    start_date: datetime = Query(..., description="Start date for export"),
    end_date: datetime = Query(..., description="End date for export"),
    db: Session = Depends(get_db)
):
    """
    Export audit logs to CSV format for external analysis.
    
    Provides compliance-ready export functionality for regulatory requirements.
    """
    from api.models.database import AuditLog as AuditLogModel
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    # Validate date range
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export period cannot exceed 90 days"
        )
    
    # Query logs
    logs = db.query(AuditLogModel).filter(
        AuditLogModel.timestamp >= start_date,
        AuditLogModel.timestamp <= end_date
    ).order_by(AuditLogModel.timestamp).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Claim ID', 'Action', 'User ID', 'Timestamp', 'Details'
    ])
    
    # Write data
    for log in logs:
        writer.writerow([
            log.id,
            log.claim_id,
            log.action,
            log.user_id or '',
            log.timestamp.isoformat(),
            str(log.details)
        ])
    
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="audit_logs_{start_date.date()}_{end_date.date()}.csv"'
        }
    )
