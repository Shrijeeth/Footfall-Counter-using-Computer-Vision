import enum

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    VIDEO_FILE = "video_file"
    LIVESTREAM = "livestream"


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)

    # Input details
    input_source = Column(String(500), nullable=False)  # File path or stream URL
    original_filename = Column(String(255), nullable=True)

    # Processing results
    entry_count = Column(Integer, default=0)
    exit_count = Column(Integer, default=0)
    total_frames_processed = Column(Integer, default=0)
    processing_duration = Column(Float, nullable=True)  # in seconds

    # Output files
    output_video_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)

    # Error handling
    error_message = Column(String(1000), nullable=True)

    # Additional metadata
    job_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="processing_jobs")
    configuration = relationship("Configuration", back_populates="processing_jobs")
