"""
Analytics API routes for FairClaimRCM

Provides analytics, metrics, and reporting capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from api.models.database import get_db
from api.models.schemas import AnalyticsMetrics, CodingPattern, PerformanceMetric
from api.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    db: Session = Depends(get_db)
):
    """
    Get key metrics for the dashboard overview.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        metrics = analytics_service.get_dashboard_metrics()
        return {
            "total_claims": metrics.get("total_claims", 0),
            "avg_processing_time": metrics.get("avg_processing_time", "0 days"),
            "approval_rate": metrics.get("approval_rate", "0%"),
            "total_revenue": metrics.get("total_revenue", "$0"),
            "monthly_trends": metrics.get("monthly_trends", []),
            "coding_accuracy": metrics.get("coding_accuracy", {}),
            "claim_status_distribution": metrics.get("claim_status_distribution", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard metrics: {str(e)}"
        )

@router.get("/coding-patterns")
async def get_coding_patterns(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    code_type: Optional[str] = Query(None, description="Filter by code type (icd10, cpt, drg)"),
    db: Session = Depends(get_db)
):
    """
    Analyze coding patterns and trends.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        patterns = analytics_service.get_coding_patterns(days, code_type)
        return {
            "patterns": patterns,
            "period": f"Last {days} days",
            "code_type": code_type or "all",
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze coding patterns: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db)
):
    """
    Get system performance metrics.
    """
    analytics_service = AnalyticsService(db)
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    try:
        metrics = analytics_service.get_performance_metrics(start_date, end_date)
        return {
            "metrics": metrics,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch performance metrics: {str(e)}"
        )

@router.get("/reimbursement-trends")
async def get_reimbursement_trends(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    group_by: str = Query("month", description="Group by: month, quarter, year"),
    db: Session = Depends(get_db)
):
    """
    Analyze reimbursement trends over time.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        trends = analytics_service.get_reimbursement_trends(months, group_by)
        return {
            "trends": trends,
            "period": f"Last {months} months",
            "group_by": group_by,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze reimbursement trends: {str(e)}"
        )

@router.get("/coding-accuracy")
async def get_coding_accuracy_report(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    coder_id: Optional[str] = Query(None, description="Filter by specific coder"),
    db: Session = Depends(get_db)
):
    """
    Generate coding accuracy report.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        accuracy_report = analytics_service.get_coding_accuracy(days, coder_id)
        return {
            "accuracy_report": accuracy_report,
            "period": f"Last {days} days",
            "coder_id": coder_id,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate accuracy report: {str(e)}"
        )

@router.get("/denial-analysis")
async def get_denial_analysis(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze claim denials and their reasons.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        denial_analysis = analytics_service.get_denial_analysis(days)
        return {
            "denial_analysis": denial_analysis,
            "period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze denials: {str(e)}"
        )

@router.get("/realtime-stats")
async def get_realtime_stats(
    db: Session = Depends(get_db)
):
    """
    Get real-time system statistics.
    """
    analytics_service = AnalyticsService(db)
    
    try:
        stats = analytics_service.get_realtime_stats()
        return {
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch real-time stats: {str(e)}"
        )
