"""
Batch Processing Routes for FairClaimRCM

Handles large-scale claim processing and bulk operations.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
import json
import csv
import io
from datetime import datetime

from api.models.database import get_db
from api.services.batch_service import BatchService
from api.models.schemas import BatchJobResponse, BatchJobStatus, ClaimBatchRequest

router = APIRouter()

@router.post("/jobs", response_model=BatchJobResponse)
async def create_batch_job(
    background_tasks: BackgroundTasks,
    batch_request: ClaimBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new batch processing job for multiple claims.
    
    - **claims**: List of claims to process
    - **job_type**: Type of batch job (coding, validation, reimbursement)
    - **options**: Additional processing options
    """
    try:
        batch_service = BatchService(db)
        job = await batch_service.create_batch_job(
            claims=batch_request.claims,
            job_type=batch_request.job_type,
            options=batch_request.options or {}
        )
        
        # Add background task to process the job
        background_tasks.add_task(
            batch_service.process_batch_job,
            job_id=job.job_id
        )
        
        return BatchJobResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            total_items=job.total_items,
            processed_items=job.processed_items,
            success_count=job.success_count,
            error_count=job.error_count,
            estimated_completion=job.estimated_completion
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create batch job: {str(e)}")

@router.post("/jobs/upload", response_model=BatchJobResponse)
async def upload_batch_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_type: str = "coding",
    db: Session = Depends(get_db)
):
    """
    Upload a CSV or JSON file for batch processing.
    
    - **file**: CSV or JSON file containing claim data
    - **job_type**: Type of processing (coding, validation, reimbursement)
    """
    try:
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        content = await file.read()
        batch_service = BatchService(db)
        
        if file.filename.endswith('.csv'):
            # Parse CSV content
            csv_content = io.StringIO(content.decode('utf-8'))
            csv_reader = csv.DictReader(csv_content)
            claims = list(csv_reader)
        else:
            # Parse JSON content
            claims = json.loads(content.decode('utf-8'))
        
        if not isinstance(claims, list):
            raise HTTPException(status_code=400, detail="File must contain an array of claims")
        
        job = await batch_service.create_batch_job(
            claims=claims,
            job_type=job_type,
            options={"source": "file_upload", "filename": file.filename}
        )
        
        # Add background task to process the job
        background_tasks.add_task(
            batch_service.process_batch_job,
            job_id=job.job_id
        )
        
        return BatchJobResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            total_items=job.total_items,
            processed_items=job.processed_items,
            success_count=job.success_count,
            error_count=job.error_count,
            estimated_completion=job.estimated_completion
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@router.get("/jobs", response_model=List[BatchJobResponse])
async def list_batch_jobs(
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List batch processing jobs with optional filtering.
    
    - **status**: Filter by job status (pending, processing, completed, failed)
    - **job_type**: Filter by job type (coding, validation, reimbursement)
    - **limit**: Maximum number of jobs to return
    """
    try:
        batch_service = BatchService(db)
        jobs = await batch_service.list_batch_jobs(
            status=status,
            job_type=job_type,
            limit=limit
        )
        
        return [
            BatchJobResponse(
                job_id=job.job_id,
                status=job.status,
                created_at=job.created_at,
                total_items=job.total_items,
                processed_items=job.processed_items,
                success_count=job.success_count,
                error_count=job.error_count,
                estimated_completion=job.estimated_completion
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list batch jobs: {str(e)}")

@router.get("/jobs/{job_id}", response_model=BatchJobStatus)
async def get_batch_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed status and results for a specific batch job.
    
    - **job_id**: Unique identifier for the batch job
    """
    try:
        batch_service = BatchService(db)
        job_status = await batch_service.get_batch_job_status(job_id)
        
        if not job_status:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        return job_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch job status: {str(e)}")

@router.post("/jobs/{job_id}/cancel")
async def cancel_batch_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a running batch job.
    
    - **job_id**: Unique identifier for the batch job
    """
    try:
        batch_service = BatchService(db)
        success = await batch_service.cancel_batch_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Batch job not found or cannot be cancelled")
        
        return {"message": "Batch job cancelled successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel batch job: {str(e)}")

@router.get("/jobs/{job_id}/download")
async def download_batch_results(
    job_id: str,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Download batch job results in specified format.
    
    - **job_id**: Unique identifier for the batch job
    - **format**: Output format (json, csv, excel)
    """
    try:
        if format not in ["json", "csv", "excel"]:
            raise HTTPException(status_code=400, detail="Supported formats: json, csv, excel")
        
        batch_service = BatchService(db)
        results = await batch_service.get_batch_results(job_id, format)
        
        if not results:
            raise HTTPException(status_code=404, detail="Batch job not found or no results available")
        
        # Return appropriate response based on format
        from fastapi.responses import Response
        
        if format == "json":
            return Response(
                content=json.dumps(results, indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={job_id}_results.json"}
            )
        elif format == "csv":
            # Convert to CSV format
            return Response(
                content=results,  # batch_service should return CSV string for this format
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={job_id}_results.csv"}
            )
        else:  # excel
            return Response(
                content=results,  # batch_service should return Excel bytes for this format
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={job_id}_results.xlsx"}
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download batch results: {str(e)}")

@router.get("/stats")
async def get_batch_processing_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get batch processing statistics for the specified period.
    
    - **days**: Number of days to include in statistics (default: 30)
    """
    try:
        batch_service = BatchService(db)
        stats = await batch_service.get_batch_statistics(days)
        
        return {
            "period_days": days,
            "total_jobs": stats.get("total_jobs", 0),
            "completed_jobs": stats.get("completed_jobs", 0),
            "failed_jobs": stats.get("failed_jobs", 0),
            "total_items_processed": stats.get("total_items_processed", 0),
            "avg_processing_time": stats.get("avg_processing_time", "0s"),
            "success_rate": stats.get("success_rate", 0.0),
            "daily_breakdown": stats.get("daily_breakdown", []),
            "popular_job_types": stats.get("popular_job_types", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch processing stats: {str(e)}")
