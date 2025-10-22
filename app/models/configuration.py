from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    # ROI Configuration (line coordinates)
    roi_x1 = Column(Integer, nullable=False)
    roi_y1 = Column(Integer, nullable=False)
    roi_x2 = Column(Integer, nullable=False)
    roi_y2 = Column(Integer, nullable=False)

    # Detection parameters
    confidence_threshold = Column(Float, default=0.5)
    debounce_frames = Column(Integer, default=50)

    # Additional settings as JSON
    additional_settings = Column(JSON, nullable=True)

    # Metadata
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="configurations")
    processing_jobs = relationship("ProcessingJob", back_populates="configuration")
