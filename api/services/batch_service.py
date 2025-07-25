"""
Batch Processing Service for FairClaimRCM

Handles large-scale batch processing of claims, including parallel processing,
job queuing, progress tracking, and result management.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import uuid
import json
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.services.coding_service import CodingService
from api.services.audit_service import AuditService
from api.models.database import Claim as ClaimModel, AuditLog as AuditLogModel

class BatchJob:
    """Represents a batch processing job."""
    
    def __init__(self, job_id: str, job_type: str, total_items: int, options: Dict[str, Any] = None):
        self.job_id = job_id
        self.job_type = job_type
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.total_items = total_items
        self.processed_items = 0
        self.success_count = 0
        self.error_count = 0
        self.results = []
        self.errors = []
        self.options = options or {}
        self.estimated_completion = None
        self.progress_percentage = 0.0

    def update_progress(self, processed: int, success: int, error: int):
        """Update job progress."""
        self.processed_items = processed
        self.success_count = success
        self.error_count = error
        self.progress_percentage = (processed / self.total_items) * 100 if self.total_items > 0 else 0

        # Estimate completion time based on current progress
        if self.started_at and processed > 0:
            elapsed = datetime.utcnow() - self.started_at
            rate = processed / elapsed.total_seconds()
            remaining_items = self.total_items - processed
            if rate > 0:
                remaining_seconds = remaining_items / rate
                self.estimated_completion = datetime.utcnow() + timedelta(seconds=remaining_seconds)

class BatchService:
    def __init__(self, db: Session):
        self.db = db
        self.coding_service = CodingService(db)
        self.audit_service = AuditService(db)
        self.active_jobs: Dict[str, BatchJob] = {}
        self.max_parallel_jobs = 5
        self.max_parallel_items = 10

    async def create_batch_job(
        self, 
        claims: List[Dict[str, Any]], 
        job_type: str, 
        options: Dict[str, Any] = None
    ) -> BatchJob:
        """
        Create a new batch processing job.
        
        Args:
            claims: List of claims to process
            job_type: Type of batch job (coding, validation, reimbursement)
            options: Additional processing options
            
        Returns:
            BatchJob: Created batch job
        """
        job_id = str(uuid.uuid4())
        job = BatchJob(
            job_id=job_id,
            job_type=job_type,
            total_items=len(claims),
            options=options
        )
        
        # Store job data temporarily (in a real implementation, use Redis or database)
        job.claims_data = claims
        self.active_jobs[job_id] = job
        
        # Log job creation
        await self.audit_service.log_activity(
            claim_id=f"batch_{job_id}",
            action="batch_job_created",
            details={
                "job_type": job_type,
                "total_items": len(claims),
                "options": options
            }
        )
        
        return job

    async def process_batch_job(self, job_id: str):
        """
        Process a batch job in the background.
        
        Args:
            job_id: Unique identifier for the batch job
        """
        if job_id not in self.active_jobs:
            return
        
        job = self.active_jobs[job_id]
        job.status = "processing"
        job.started_at = datetime.utcnow()
        
        try:
            if job.job_type == "coding":
                await self._process_coding_batch(job)
            elif job.job_type == "validation":
                await self._process_validation_batch(job)
            elif job.job_type == "reimbursement":
                await self._process_reimbursement_batch(job)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")
            
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            
        except Exception as e:
            job.status = "failed"
            job.errors.append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Log job completion
        await self.audit_service.log_activity(
            claim_id=f"batch_{job_id}",
            action="batch_job_completed",
            details={
                "status": job.status,
                "processed_items": job.processed_items,
                "success_count": job.success_count,
                "error_count": job.error_count,
                "duration": (job.completed_at - job.started_at).total_seconds() if job.completed_at else None
            }
        )

    async def _process_coding_batch(self, job: BatchJob):
        """Process a batch coding job."""
        with ThreadPoolExecutor(max_workers=self.max_parallel_items) as executor:
            futures = []
            
            for i, claim_data in enumerate(job.claims_data):
                future = executor.submit(self._process_single_coding, claim_data, i)
                futures.append(future)
            
            processed = 0
            success = 0
            error = 0
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result["success"]:
                        success += 1
                        job.results.append(result["data"])
                    else:
                        error += 1
                        job.errors.append(result["error"])
                except Exception as e:
                    error += 1
                    job.errors.append({
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                processed += 1
                job.update_progress(processed, success, error)

    def _process_single_coding(self, claim_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process a single claim for coding."""
        try:
            clinical_text = claim_data.get("clinical_text", "")
            if not clinical_text:
                return {
                    "success": False,
                    "error": {
                        "index": index,
                        "claim_id": claim_data.get("claim_id", f"claim_{index}"),
                        "error": "Missing clinical text",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            
            # Generate coding recommendations
            recommendations = self.coding_service.generate_recommendations(clinical_text)
            
            return {
                "success": True,
                "data": {
                    "index": index,
                    "claim_id": claim_data.get("claim_id", f"claim_{index}"),
                    "recommendations": recommendations,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "index": index,
                    "claim_id": claim_data.get("claim_id", f"claim_{index}"),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    async def _process_validation_batch(self, job: BatchJob):
        """Process a batch validation job."""
        processed = 0
        success = 0
        error = 0
        
        for i, claim_data in enumerate(job.claims_data):
            try:
                # Validate claim codes
                codes = claim_data.get("codes", [])
                validation_result = self.coding_service.validate_codes(codes)
                
                job.results.append({
                    "index": i,
                    "claim_id": claim_data.get("claim_id", f"claim_{i}"),
                    "validation": validation_result,
                    "processed_at": datetime.utcnow().isoformat()
                })
                success += 1
                
            except Exception as e:
                job.errors.append({
                    "index": i,
                    "claim_id": claim_data.get("claim_id", f"claim_{i}"),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                error += 1
            
            processed += 1
            job.update_progress(processed, success, error)

    async def _process_reimbursement_batch(self, job: BatchJob):
        """Process a batch reimbursement calculation job."""
        processed = 0
        success = 0
        error = 0
        
        for i, claim_data in enumerate(job.claims_data):
            try:
                # Calculate reimbursement
                codes = claim_data.get("codes", [])
                reimbursement = self._calculate_reimbursement(codes)
                
                job.results.append({
                    "index": i,
                    "claim_id": claim_data.get("claim_id", f"claim_{i}"),
                    "reimbursement": reimbursement,
                    "processed_at": datetime.utcnow().isoformat()
                })
                success += 1
                
            except Exception as e:
                job.errors.append({
                    "index": i,
                    "claim_id": claim_data.get("claim_id", f"claim_{i}"),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                error += 1
            
            processed += 1
            job.update_progress(processed, success, error)

    def _calculate_reimbursement(self, codes: List[str]) -> Dict[str, Any]:
        """Calculate reimbursement for a set of codes (mock implementation)."""
        total_amount = 0
        code_details = []
        
        for code in codes:
            # Mock reimbursement calculation
            if code.startswith("99"):  # CPT codes
                amount = 150.00  # Base office visit
            elif code.startswith("I"):  # ICD-10 diagnosis
                amount = 0  # Diagnoses don't have direct reimbursement
            else:
                amount = 100.00  # Default amount
            
            total_amount += amount
            code_details.append({
                "code": code,
                "amount": amount,
                "description": f"Reimbursement for {code}"
            })
        
        return {
            "total_amount": total_amount,
            "code_details": code_details,
            "calculated_at": datetime.utcnow().isoformat()
        }

    async def list_batch_jobs(
        self, 
        status: Optional[str] = None, 
        job_type: Optional[str] = None, 
        limit: int = 50
    ) -> List[BatchJob]:
        """List batch jobs with optional filtering."""
        jobs = list(self.active_jobs.values())
        
        # Apply filters
        if status:
            jobs = [job for job in jobs if job.status == status]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        
        # Sort by creation time (newest first) and limit
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]

    async def get_batch_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a specific batch job."""
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        return {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "total_items": job.total_items,
            "processed_items": job.processed_items,
            "success_count": job.success_count,
            "error_count": job.error_count,
            "progress_percentage": job.progress_percentage,
            "estimated_completion": job.estimated_completion.isoformat() if job.estimated_completion else None,
            "results": job.results,
            "errors": job.errors,
            "options": job.options
        }

    async def cancel_batch_job(self, job_id: str) -> bool:
        """Cancel a running batch job."""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status in ["completed", "failed", "cancelled"]:
            return False
        
        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        
        await self.audit_service.log_activity(
            claim_id=f"batch_{job_id}",
            action="batch_job_cancelled",
            details={"cancelled_at": job.completed_at.isoformat()}
        )
        
        return True

    async def get_batch_results(self, job_id: str, format: str = "json") -> Optional[Any]:
        """Get batch job results in specified format."""
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        if job.status != "completed":
            return None
        
        if format == "json":
            return {
                "job_id": job.job_id,
                "status": job.status,
                "results": job.results,
                "errors": job.errors,
                "summary": {
                    "total_items": job.total_items,
                    "success_count": job.success_count,
                    "error_count": job.error_count,
                    "processing_time": (job.completed_at - job.started_at).total_seconds()
                }
            }
        
        # For CSV and Excel formats, return formatted strings/bytes
        # This would be implemented based on specific requirements
        return json.dumps(job.results)

    async def get_batch_statistics(self, days: int) -> Dict[str, Any]:
        """Get batch processing statistics for the specified period."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter jobs within the time period
        period_jobs = [
            job for job in self.active_jobs.values()
            if job.created_at >= cutoff_date
        ]
        
        total_jobs = len(period_jobs)
        completed_jobs = len([job for job in period_jobs if job.status == "completed"])
        failed_jobs = len([job for job in period_jobs if job.status == "failed"])
        
        total_items_processed = sum(job.processed_items for job in period_jobs)
        
        # Calculate average processing time
        completed_with_times = [
            job for job in period_jobs 
            if job.status == "completed" and job.started_at and job.completed_at
        ]
        
        if completed_with_times:
            avg_time_seconds = sum(
                (job.completed_at - job.started_at).total_seconds()
                for job in completed_with_times
            ) / len(completed_with_times)
            avg_processing_time = f"{avg_time_seconds:.1f}s"
        else:
            avg_processing_time = "0s"
        
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0.0
        
        # Job type distribution
        job_types = {}
        for job in period_jobs:
            job_types[job.job_type] = job_types.get(job.job_type, 0) + 1
        
        popular_job_types = [
            {"type": job_type, "count": count}
            for job_type, count in sorted(job_types.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_items_processed": total_items_processed,
            "avg_processing_time": avg_processing_time,
            "success_rate": success_rate,
            "popular_job_types": popular_job_types,
            "daily_breakdown": []  # Could be implemented for more detailed stats
        }
