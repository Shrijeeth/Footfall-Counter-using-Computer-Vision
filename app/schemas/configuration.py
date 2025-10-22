from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ConfigurationBase(BaseModel):
    name: str
    description: Optional[str] = None
    roi_x1: int
    roi_y1: int
    roi_x2: int
    roi_y2: int
    confidence_threshold: float = 0.5
    debounce_frames: int = 50
    additional_settings: Optional[Dict[str, Any]] = None
    is_default: bool = False


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    roi_x1: Optional[int] = None
    roi_y1: Optional[int] = None
    roi_x2: Optional[int] = None
    roi_y2: Optional[int] = None
    confidence_threshold: Optional[float] = None
    debounce_frames: Optional[int] = None
    additional_settings: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class ConfigurationResponse(ConfigurationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
