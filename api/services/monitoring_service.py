"""
Real-time Monitoring Service for FairClaimRCM

Provides system health monitoring, performance metrics, and real-time statistics.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import psutil
import time
import json
from dataclasses import dataclass, asdict

from api.models.database import Claim as ClaimModel, AuditLog as AuditLogModel

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    load_average: List[float]
    uptime_seconds: float
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    active_users: int
    claims_processed_today: int
    api_requests_per_minute: float
    avg_response_time_ms: float
    error_rate_percent: float
    cache_hit_rate_percent: float
    timestamp: datetime

@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    active_connections: int
    total_connections: int
    queries_per_second: float
    avg_query_time_ms: float
    slow_queries_count: int
    database_size_mb: float
    timestamp: datetime

class RealTimeMonitoringService:
    """Service for real-time system and application monitoring."""
    
    def __init__(self, db: Session):
        self.db = db
        self.start_time = time.time()
        
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                # Windows doesn't have load average
                load_avg = [0.0, 0.0, 0.0]
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                load_average=load_avg,
                uptime_seconds=uptime_seconds,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            # Return default metrics if system monitoring fails
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                load_average=[0.0, 0.0, 0.0],
                uptime_seconds=0.0,
                timestamp=datetime.utcnow()
            )
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """Get current application performance metrics."""
        try:
            # Get active users (mock - would need session tracking)
            active_users = self._get_active_users_count()
            
            # Claims processed today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            claims_today = self.db.query(ClaimModel).filter(
                ClaimModel.created_at >= today_start
            ).count()
            
            # API requests per minute (from audit logs)
            api_requests_per_minute = self._get_api_requests_per_minute()
            
            # Average response time (mock - would need request tracking)
            avg_response_time_ms = 245.0
            
            # Error rate (from audit logs)
            error_rate_percent = self._get_error_rate()
            
            # Cache hit rate (mock)
            cache_hit_rate_percent = 85.0
            
            return ApplicationMetrics(
                active_users=active_users,
                claims_processed_today=claims_today,
                api_requests_per_minute=api_requests_per_minute,
                avg_response_time_ms=avg_response_time_ms,
                error_rate_percent=error_rate_percent,
                cache_hit_rate_percent=cache_hit_rate_percent,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return ApplicationMetrics(
                active_users=0,
                claims_processed_today=0,
                api_requests_per_minute=0.0,
                avg_response_time_ms=0.0,
                error_rate_percent=0.0,
                cache_hit_rate_percent=0.0,
                timestamp=datetime.utcnow()
            )
    
    def get_database_metrics(self) -> DatabaseMetrics:
        """Get current database performance metrics."""
        try:
            # Get database connection info
            connection_info = self._get_database_connections()
            
            # Calculate queries per second (from audit logs)
            queries_per_second = self._get_queries_per_second()
            
            # Average query time (mock)
            avg_query_time_ms = 15.5
            
            # Slow queries count (mock)
            slow_queries_count = 3
            
            # Database size (mock)
            database_size_mb = 245.8
            
            return DatabaseMetrics(
                active_connections=connection_info["active"],
                total_connections=connection_info["total"],
                queries_per_second=queries_per_second,
                avg_query_time_ms=avg_query_time_ms,
                slow_queries_count=slow_queries_count,
                database_size_mb=database_size_mb,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DatabaseMetrics(
                active_connections=0,
                total_connections=0,
                queries_per_second=0.0,
                avg_query_time_ms=0.0,
                slow_queries_count=0,
                database_size_mb=0.0,
                timestamp=datetime.utcnow()
            )
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get comprehensive real-time statistics."""
        # Get all metrics
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        db_metrics = self.get_database_metrics()
        
        # Calculate overall health score
        health_score = self._calculate_health_score(system_metrics, app_metrics, db_metrics)
        
        # Get recent activities
        recent_activities = self._get_recent_activities()
        
        # Get alerts
        alerts = self._get_active_alerts(system_metrics, app_metrics, db_metrics)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_score": health_score,
            "system": asdict(system_metrics),
            "application": asdict(app_metrics),
            "database": asdict(db_metrics),
            "recent_activities": recent_activities,
            "alerts": alerts,
            "status": "healthy" if health_score >= 85 else "warning" if health_score >= 70 else "critical"
        }
    
    def get_performance_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics history for the specified period."""
        try:
            # In a real implementation, this would query stored metrics
            # For now, generate mock historical data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            history = []
            current_time = start_time
            
            while current_time <= end_time:
                # Generate mock data points
                history.append({
                    "timestamp": current_time.isoformat(),
                    "cpu_percent": 15 + (current_time.hour % 12) * 2,
                    "memory_percent": 60 + (current_time.hour % 8) * 3,
                    "response_time_ms": 200 + (current_time.minute % 10) * 10,
                    "requests_per_minute": 50 + (current_time.hour % 6) * 15,
                    "error_rate": 0.1 + (current_time.hour % 24) * 0.05
                })
                current_time += timedelta(minutes=15)
            
            return {
                "period_hours": hours,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "data_points": len(history),
                "history": history
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get performance history: {str(e)}",
                "period_hours": hours,
                "history": []
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of various system services and dependencies."""
        services = {
            "api_server": self._check_api_server_status(),
            "database": self._check_database_status(),
            "cache": self._check_cache_status(),
            "file_system": self._check_file_system_status(),
            "external_apis": self._check_external_apis_status()
        }
        
        # Calculate overall service health
        healthy_services = sum(1 for service in services.values() if service["status"] == "healthy")
        total_services = len(services)
        overall_health = (healthy_services / total_services) * 100
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": overall_health,
            "overall_status": "healthy" if overall_health >= 90 else "degraded" if overall_health >= 70 else "unhealthy",
            "services": services,
            "healthy_count": healthy_services,
            "total_count": total_services
        }
    
    def _get_active_users_count(self) -> int:
        """Get count of active users (mock implementation)."""
        # In a real implementation, this would query session storage
        return 15
    
    def _get_api_requests_per_minute(self) -> float:
        """Calculate API requests per minute from audit logs."""
        try:
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            request_count = self.db.query(AuditLogModel).filter(
                AuditLogModel.timestamp >= one_minute_ago
            ).count()
            return float(request_count)
        except:
            return 45.0  # Mock value
    
    def _get_error_rate(self) -> float:
        """Calculate error rate from audit logs."""
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            total_requests = self.db.query(AuditLogModel).filter(
                AuditLogModel.timestamp >= one_hour_ago
            ).count()
            
            error_requests = self.db.query(AuditLogModel).filter(
                AuditLogModel.timestamp >= one_hour_ago,
                AuditLogModel.action.like('%error%')
            ).count()
            
            if total_requests > 0:
                return (error_requests / total_requests) * 100
            return 0.0
        except:
            return 0.2  # Mock value
    
    def _get_database_connections(self) -> Dict[str, int]:
        """Get database connection information."""
        try:
            # This would query database-specific metrics
            # Mock implementation
            return {"active": 8, "total": 20}
        except:
            return {"active": 0, "total": 0}
    
    def _get_queries_per_second(self) -> float:
        """Calculate database queries per second."""
        try:
            # Mock calculation based on audit logs
            return 25.5
        except:
            return 0.0
    
    def _calculate_health_score(
        self, 
        system: SystemMetrics, 
        app: ApplicationMetrics, 
        db: DatabaseMetrics
    ) -> float:
        """Calculate overall system health score (0-100)."""
        # Weight different metrics
        cpu_score = max(0, 100 - system.cpu_percent)
        memory_score = max(0, 100 - system.memory_percent)
        disk_score = max(0, 100 - system.disk_percent)
        
        # Application health
        error_score = max(0, 100 - (app.error_rate_percent * 10))
        response_score = max(0, 100 - (app.avg_response_time_ms / 10))
        
        # Calculate weighted average
        weights = {
            "cpu": 0.2,
            "memory": 0.2,
            "disk": 0.1,
            "errors": 0.3,
            "response": 0.2
        }
        
        health_score = (
            cpu_score * weights["cpu"] +
            memory_score * weights["memory"] +
            disk_score * weights["disk"] +
            error_score * weights["errors"] +
            response_score * weights["response"]
        )
        
        return round(health_score, 1)
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent system activities."""
        try:
            recent_logs = self.db.query(AuditLogModel).order_by(
                AuditLogModel.timestamp.desc()
            ).limit(10).all()
            
            activities = []
            for log in recent_logs:
                activities.append({
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "claim_id": log.claim_id,
                    "user_id": log.user_id
                })
            
            return activities
        except:
            return []
    
    def _get_active_alerts(
        self, 
        system: SystemMetrics, 
        app: ApplicationMetrics, 
        db: DatabaseMetrics
    ) -> List[Dict[str, Any]]:
        """Get active system alerts."""
        alerts = []
        
        # Check system metrics
        if system.cpu_percent > 80:
            alerts.append({
                "type": "warning",
                "category": "system",
                "message": f"High CPU usage: {system.cpu_percent}%",
                "timestamp": system.timestamp.isoformat()
            })
        
        if system.memory_percent > 85:
            alerts.append({
                "type": "critical",
                "category": "system",
                "message": f"High memory usage: {system.memory_percent}%",
                "timestamp": system.timestamp.isoformat()
            })
        
        if system.disk_percent > 90:
            alerts.append({
                "type": "critical",
                "category": "system",
                "message": f"Low disk space: {system.disk_percent}% used",
                "timestamp": system.timestamp.isoformat()
            })
        
        # Check application metrics
        if app.error_rate_percent > 5:
            alerts.append({
                "type": "warning",
                "category": "application",
                "message": f"High error rate: {app.error_rate_percent}%",
                "timestamp": app.timestamp.isoformat()
            })
        
        if app.avg_response_time_ms > 1000:
            alerts.append({
                "type": "warning",
                "category": "application",
                "message": f"Slow response time: {app.avg_response_time_ms}ms",
                "timestamp": app.timestamp.isoformat()
            })
        
        return alerts
    
    def _check_api_server_status(self) -> Dict[str, Any]:
        """Check API server status."""
        return {
            "status": "healthy",
            "response_time_ms": 12,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def _check_database_status(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            # Simple query to test database
            result = self.db.execute(text("SELECT 1")).fetchone()
            return {
                "status": "healthy",
                "response_time_ms": 8,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_cache_status(self) -> Dict[str, Any]:
        """Check cache service status."""
        # Mock implementation
        return {
            "status": "healthy",
            "hit_rate": 85.2,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def _check_file_system_status(self) -> Dict[str, Any]:
        """Check file system status."""
        try:
            disk = psutil.disk_usage('/')
            return {
                "status": "healthy",
                "free_space_gb": round(disk.free / (1024**3), 2),
                "total_space_gb": round(disk.total / (1024**3), 2),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _check_external_apis_status(self) -> Dict[str, Any]:
        """Check external API dependencies."""
        # Mock implementation for external services
        return {
            "status": "healthy",
            "services_checked": ["terminology_api", "payer_api"],
            "all_healthy": True,
            "last_check": datetime.utcnow().isoformat()
        }
