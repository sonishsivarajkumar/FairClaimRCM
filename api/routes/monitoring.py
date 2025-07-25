"""
Real-time Monitoring Routes for FairClaimRCM

Provides system health monitoring, performance metrics, and real-time statistics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from api.models.database import get_db
from api.services.monitoring_service import RealTimeMonitoringService

router = APIRouter()

@router.get("/health")
async def get_system_health(db: Session = Depends(get_db)):
    """
    Get comprehensive system health status.
    
    Returns overall health score, system metrics, and active alerts.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        health_data = monitoring_service.get_real_time_stats()
        
        return health_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@router.get("/metrics/system")
async def get_system_metrics(db: Session = Depends(get_db)):
    """
    Get current system performance metrics.
    
    Returns CPU, memory, disk usage, and load average.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        system_metrics = monitoring_service.get_system_metrics()
        
        return {
            "timestamp": system_metrics.timestamp.isoformat(),
            "cpu_percent": system_metrics.cpu_percent,
            "memory_percent": system_metrics.memory_percent,
            "disk_percent": system_metrics.disk_percent,
            "load_average": system_metrics.load_average,
            "uptime_seconds": system_metrics.uptime_seconds,
            "uptime_human": f"{int(system_metrics.uptime_seconds // 3600)}h {int((system_metrics.uptime_seconds % 3600) // 60)}m"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@router.get("/metrics/application")
async def get_application_metrics(db: Session = Depends(get_db)):
    """
    Get current application performance metrics.
    
    Returns user activity, API performance, and error rates.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        app_metrics = monitoring_service.get_application_metrics()
        
        return {
            "timestamp": app_metrics.timestamp.isoformat(),
            "active_users": app_metrics.active_users,
            "claims_processed_today": app_metrics.claims_processed_today,
            "api_requests_per_minute": app_metrics.api_requests_per_minute,
            "avg_response_time_ms": app_metrics.avg_response_time_ms,
            "error_rate_percent": app_metrics.error_rate_percent,
            "cache_hit_rate_percent": app_metrics.cache_hit_rate_percent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application metrics: {str(e)}")

@router.get("/metrics/database")
async def get_database_metrics(db: Session = Depends(get_db)):
    """
    Get current database performance metrics.
    
    Returns connection info, query performance, and database size.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        db_metrics = monitoring_service.get_database_metrics()
        
        return {
            "timestamp": db_metrics.timestamp.isoformat(),
            "active_connections": db_metrics.active_connections,
            "total_connections": db_metrics.total_connections,
            "connection_utilization": f"{(db_metrics.active_connections / max(db_metrics.total_connections, 1) * 100):.1f}%",
            "queries_per_second": db_metrics.queries_per_second,
            "avg_query_time_ms": db_metrics.avg_query_time_ms,
            "slow_queries_count": db_metrics.slow_queries_count,
            "database_size_mb": db_metrics.database_size_mb
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database metrics: {str(e)}")

@router.get("/performance/history")
async def get_performance_history(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get performance metrics history for the specified period.
    
    - **hours**: Number of hours of history to retrieve (default: 24, max: 168)
    """
    try:
        if hours > 168:  # Limit to 1 week
            raise HTTPException(status_code=400, detail="Maximum history period is 168 hours (1 week)")
        
        if hours < 1:
            raise HTTPException(status_code=400, detail="Minimum history period is 1 hour")
        
        monitoring_service = RealTimeMonitoringService(db)
        history = monitoring_service.get_performance_history(hours)
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance history: {str(e)}")

@router.get("/services/status")
async def get_service_status(db: Session = Depends(get_db)):
    """
    Get status of all system services and dependencies.
    
    Returns health status for API server, database, cache, file system, and external APIs.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        service_status = monitoring_service.get_service_status()
        
        return service_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service status: {str(e)}")

@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get active system alerts with optional filtering.
    
    - **severity**: Filter by alert severity (info, warning, critical)
    - **category**: Filter by alert category (system, application, database)
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        real_time_stats = monitoring_service.get_real_time_stats()
        alerts = real_time_stats.get("alerts", [])
        
        # Apply filters
        if severity:
            alerts = [alert for alert in alerts if alert.get("type") == severity]
        
        if category:
            alerts = [alert for alert in alerts if alert.get("category") == category]
        
        return {
            "timestamp": real_time_stats["timestamp"],
            "total_alerts": len(alerts),
            "alerts": alerts,
            "filters_applied": {
                "severity": severity,
                "category": category
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/dashboard")
async def get_monitoring_dashboard(db: Session = Depends(get_db)):
    """
    Get comprehensive monitoring dashboard data.
    
    Returns all key metrics, alerts, and status information in a single response.
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        
        # Get all monitoring data
        real_time_stats = monitoring_service.get_real_time_stats()
        service_status = monitoring_service.get_service_status()
        
        dashboard = {
            "timestamp": real_time_stats["timestamp"],
            "overall_health": {
                "score": real_time_stats["health_score"],
                "status": real_time_stats["status"],
                "service_health": service_status["overall_health"]
            },
            "system_metrics": real_time_stats["system"],
            "application_metrics": real_time_stats["application"],
            "database_metrics": real_time_stats["database"],
            "service_status": service_status["services"],
            "active_alerts": real_time_stats["alerts"],
            "recent_activities": real_time_stats["recent_activities"][:5],  # Limit to 5 most recent
            "summary": {
                "alerts_count": len(real_time_stats["alerts"]),
                "healthy_services": service_status["healthy_count"],
                "total_services": service_status["total_count"],
                "uptime_hours": round(real_time_stats["system"]["uptime_seconds"] / 3600, 1)
            }
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring dashboard: {str(e)}")

@router.post("/alerts/acknowledge")
async def acknowledge_alert(
    alert_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert (mark as seen/handled).
    
    - **alert_data**: Alert information to acknowledge
    """
    try:
        # In a real implementation, this would update alert status in storage
        # For now, just return success
        
        return {
            "message": "Alert acknowledged",
            "alert_id": alert_data.get("id", "unknown"),
            "acknowledged_at": RealTimeMonitoringService(db).get_real_time_stats()["timestamp"],
            "status": "acknowledged"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.get("/statistics/live")
async def get_live_statistics(db: Session = Depends(get_db)):
    """
    Get live system statistics for real-time updates.
    
    Returns key metrics optimized for frequent polling (every 5-10 seconds).
    """
    try:
        monitoring_service = RealTimeMonitoringService(db)
        
        # Get lightweight metrics for frequent updates
        system_metrics = monitoring_service.get_system_metrics()
        app_metrics = monitoring_service.get_application_metrics()
        
        live_stats = {
            "timestamp": system_metrics.timestamp.isoformat(),
            "cpu_percent": system_metrics.cpu_percent,
            "memory_percent": system_metrics.memory_percent,
            "active_users": app_metrics.active_users,
            "requests_per_minute": app_metrics.api_requests_per_minute,
            "response_time_ms": app_metrics.avg_response_time_ms,
            "error_rate": app_metrics.error_rate_percent,
            "status": "healthy" if system_metrics.cpu_percent < 80 and system_metrics.memory_percent < 85 else "warning"
        }
        
        return live_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live statistics: {str(e)}")

@router.get("/export")
async def export_monitoring_data(
    format: str = "json",
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Export monitoring data for external analysis.
    
    - **format**: Export format (json, csv)
    - **hours**: Hours of data to export
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Supported formats: json, csv")
        
        monitoring_service = RealTimeMonitoringService(db)
        
        # Get comprehensive data
        current_stats = monitoring_service.get_real_time_stats()
        performance_history = monitoring_service.get_performance_history(hours)
        service_status = monitoring_service.get_service_status()
        
        export_data = {
            "export_timestamp": current_stats["timestamp"],
            "export_period_hours": hours,
            "current_status": current_stats,
            "performance_history": performance_history,
            "service_status": service_status
        }
        
        if format == "json":
            return export_data
        else:  # CSV format
            # For CSV, return a simplified tabular format
            # In a real implementation, this would generate proper CSV
            return {
                "message": "CSV export not yet implemented",
                "data": export_data
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export monitoring data: {str(e)}")
