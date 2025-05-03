# api/routers/system.py - Router for system management endpoints
from fastapi import APIRouter, BackgroundTasks, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.models.system import SystemStatusResponse, PipelineStatusResponse, PipelineRunRequest
from api.dependencies.db import get_db
from api.dependencies.auth import validate_admin
from scripts.run_daily_pipeline import run_daily_pipeline
from db.models.prediction_results import PredictionResult

router = APIRouter()


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(db: Session = Depends(get_db), current_user=Depends(validate_admin)):
    """Get current system status and statistics"""
    # Get database stats
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    # Latest predictions
    total_predictions = db.query(PredictionResult).count()
    today_predictions = db.query(PredictionResult).filter(PredictionResult.date == today).count()
    yesterday_predictions = db.query(PredictionResult).filter(PredictionResult.date == yesterday).count()

    # Verified predictions
    verified_count = db.query(PredictionResult).filter(PredictionResult.verified).count()

    verified_percent = (verified_count / total_predictions * 100) if total_predictions > 0 else 0

    # Direction predictions
    direction_count = db.query(PredictionResult).filter(PredictionResult.direction_prediction.isnot(None)).count()

    # Recent model training activity (placeholder - would need a model training log table)
    recent_training = 0

    # Check disk usage of model directory
    import os
    from core.config import DAILY_MODELS_DIR

    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(DAILY_MODELS_DIR):
        for file in files:
            if file.endswith(".pkl"):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1

    # Convert to MB
    total_size_mb = total_size / (1024 * 1024)

    return SystemStatusResponse(status="healthy", server_time=datetime.now(), database_status="connected", total_predictions=total_predictions, today_predictions=today_predictions, yesterday_predictions=yesterday_predictions, verified_predictions=verified_count, verified_prediction_percent=verified_percent, direction_predictions=direction_count, recent_model_training_count=recent_training, model_directory_size_mb=total_size_mb, model_file_count=file_count)


@router.post("/run-pipeline", response_model=PipelineStatusResponse)
async def trigger_pipeline_run(background_tasks: BackgroundTasks, request: PipelineRunRequest = PipelineRunRequest(), current_user=Depends(validate_admin)):
    """Trigger a run of the daily pipeline"""
    # Run the pipeline in the background
    background_tasks.add_task(run_daily_pipeline_task, force=request.force, steps=request.steps)

    return PipelineStatusResponse(status="started", message="Daily pipeline started in background", start_time=datetime.now(), requested_by=current_user.username, estimated_duration_minutes=30, steps=request.steps if request.steps else ["all"])


async def run_daily_pipeline_task(force: bool = False, steps: Optional[list] = None):
    """Run the daily pipeline as a background task"""
    try:
        # Run the pipeline
        success = run_daily_pipeline()

        # Log the result
        print(f"[SYSTEM] Pipeline run completed with success={success}")

        # In a production system, you would store the result in a database
        # and provide a way to query the status of the pipeline run

    except Exception as e:
        print(f"[ERROR] Pipeline run failed: {str(e)}")
