from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.models.processing_job import JobStatus, JobType


class ProcessingJobBase(BaseModel):
    job_type: JobType
    input_source: str
    original_filename: Optional[str] = None


class ProcessingJobCreate(ProcessingJobBase):
    configuration_id: int


class ProcessingJobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    entry_count: Optional[int] = None
    exit_count: Optional[int] = None
    total_frames_processed: Optional[int] = None
    processing_duration: Optional[float] = None
    output_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    error_message: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None


class ProcessingJobResponse(ProcessingJobBase):
    id: int
    status: JobStatus
    entry_count: int
    exit_count: int
    total_frames_processed: int
    processing_duration: Optional[float] = None
    output_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    error_message: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: int
    configuration_id: int

    class Config:
        from_attributes = True


class VideoProcessingRequest(BaseModel):
    configuration_id: int
    confidence_threshold: Optional[float] = None
    debounce_frames: Optional[int] = None


class LivestreamProcessingRequest(BaseModel):
    stream_url: str
    configuration_id: int
    max_duration: Optional[int] = None
    confidence_threshold: Optional[float] = None
    debounce_frames: Optional[int] = None
