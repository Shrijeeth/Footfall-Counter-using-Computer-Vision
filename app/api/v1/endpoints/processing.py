import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.models.configuration import Configuration
from app.models.processing_job import JobStatus, JobType, ProcessingJob
from app.models.user import User
from app.schemas.processing_job import (
    LivestreamProcessingRequest,
    ProcessingJobResponse,
)
from app.services.video_processor import VideoProcessor

router = APIRouter()

# Ensure upload and static directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)

video_processor = VideoProcessor()


def process_video_background(
    job_id: int,
    video_path: str,
    roi_coords: tuple,
    confidence: float,
    debounce_frames: int,
    db_session_factory,
):
    """Background task for processing video files."""
    db = db_session_factory()
    try:
        # Update job status to processing
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()

        # Generate output paths
        output_filename = f"processed_{job_id}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(settings.STATIC_DIR, output_filename)

        thumbnail_filename = f"thumb_{job_id}_{uuid.uuid4().hex[:8]}.jpg"
        thumbnail_path = os.path.join(settings.STATIC_DIR, thumbnail_filename)

        # Process video
        result = video_processor.process_video_file(
            video_path=video_path,
            roi_coords=roi_coords,
            confidence=confidence,
            debounce_frames=debounce_frames,
            output_path=output_path,
        )

        # Create thumbnail
        video_processor.create_thumbnail(video_path, thumbnail_path, roi_coords)

        # Update job with results
        job.status = JobStatus.COMPLETED
        job.entry_count = result["entry_count"]
        job.exit_count = result["exit_count"]
        job.total_frames_processed = result["total_frames"]
        job.processing_duration = result["processing_duration"]
        job.output_video_path = f"/static/{output_filename}"
        job.thumbnail_path = f"/static/{thumbnail_filename}"
        job.completed_at = datetime.utcnow()
        job.job_metadata = {
            "fps": result["fps"],
            "confidence": confidence,
            "debounce_frames": debounce_frames,
        }

        db.commit()

    except Exception as e:
        # Update job with error
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()


@router.post("/upload-video", response_model=ProcessingJobResponse)
async def upload_and_process_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config_id: int = Form(..., alias="config_id"),
    confidence_threshold: float = Form(None),
    debounce_frames: int = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a video file and start processing."""
    # Validate file
    if not file.content_type or not file.content_type.startswith("video/"):
        # Also check file extension as fallback
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        file_ext = Path(file.filename).suffix.lower()
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"]
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=400,
                detail="File must be a video (mp4, avi, mov, mkv, webm, flv)",
            )

    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Get configuration
    config = (
        db.query(Configuration)
        .filter(
            Configuration.id == config_id,
            Configuration.owner_id == current_user.id,
        )
        .first()
    )

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Save uploaded file
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Create processing job
    job = ProcessingJob(
        job_type=JobType.VIDEO_FILE,
        input_source=file_path,
        original_filename=file.filename,
        user_id=current_user.id,
        configuration_id=config.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Start background processing
    roi_coords = (config.roi_x1, config.roi_y1, config.roi_x2, config.roi_y2)
    confidence = confidence_threshold or config.confidence_threshold
    debounce_frames = debounce_frames or config.debounce_frames

    background_tasks.add_task(
        process_video_background,
        job.id,
        file_path,
        roi_coords,
        confidence,
        debounce_frames,
        lambda: Session(bind=db.bind),
    )

    return job


@router.post("/livestream", response_model=ProcessingJobResponse)
def process_livestream(
    request: LivestreamProcessingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Process a livestream."""
    # Get configuration
    config = (
        db.query(Configuration)
        .filter(
            Configuration.id == request.configuration_id,
            Configuration.owner_id == current_user.id,
        )
        .first()
    )

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Create processing job
    job = ProcessingJob(
        job_type=JobType.LIVESTREAM,
        input_source=request.stream_url,
        user_id=current_user.id,
        configuration_id=config.id,
        status=JobStatus.PROCESSING,
        started_at=datetime.utcnow(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        # Process livestream
        roi_coords = (config.roi_x1, config.roi_y1, config.roi_x2, config.roi_y2)
        confidence = request.confidence_threshold or config.confidence_threshold
        debounce_frames = request.debounce_frames or config.debounce_frames

        result = video_processor.process_livestream(
            stream_url=request.stream_url,
            roi_coords=roi_coords,
            confidence=confidence,
            debounce_frames=debounce_frames,
            max_duration=request.max_duration,
        )

        # Update job with results
        job.status = JobStatus.COMPLETED
        job.entry_count = result["entry_count"]
        job.exit_count = result["exit_count"]
        job.total_frames_processed = result["total_frames"]
        job.processing_duration = result["processing_duration"]
        job.completed_at = datetime.utcnow()
        job.job_metadata = {
            "confidence": confidence,
            "debounce_frames": debounce_frames,
            "max_duration": request.max_duration,
        }

        db.commit()

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return job


@router.get("/jobs", response_model=List[ProcessingJobResponse])
def get_processing_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all processing jobs for the current user."""
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.user_id == current_user.id)
        .order_by(ProcessingJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return jobs


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
def get_processing_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific processing job."""
    job = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.id == job_id, ProcessingJob.user_id == current_user.id)
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/jobs/{job_id}/download")
def download_processed_video(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download the processed video file."""
    job = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.id == job_id, ProcessingJob.user_id == current_user.id)
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.output_video_path:
        raise HTTPException(status_code=404, detail="Processed video not available")

    # Remove the /static/ prefix to get the actual file path
    file_path = job.output_video_path.replace("/static/", "")
    full_path = os.path.join(settings.STATIC_DIR, file_path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=full_path,
        filename=f"processed_{job.original_filename or f'job_{job_id}.mp4'}",
        media_type="video/mp4",
    )
