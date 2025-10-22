from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.configuration import Configuration
from app.models.user import User
from app.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationResponse,
    ConfigurationUpdate,
)

router = APIRouter()


@router.post("/", response_model=ConfigurationResponse)
def create_configuration(
    config: ConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new configuration."""
    # If this is set as default, unset other defaults for this user
    if config.is_default:
        db.query(Configuration).filter(
            Configuration.owner_id == current_user.id, Configuration.is_default
        ).update({"is_default": False})

    db_config = Configuration(**config.dict(), owner_id=current_user.id)

    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return db_config


@router.get("/", response_model=List[ConfigurationResponse])
def read_configurations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all configurations for the current user."""
    configurations = (
        db.query(Configuration)
        .filter(Configuration.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return configurations


@router.get("/{config_id}", response_model=ConfigurationResponse)
def read_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific configuration."""
    config = (
        db.query(Configuration)
        .filter(
            Configuration.id == config_id, Configuration.owner_id == current_user.id
        )
        .first()
    )

    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")

    return config


@router.put("/{config_id}", response_model=ConfigurationResponse)
def update_configuration(
    config_id: int,
    config_update: ConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a configuration."""
    config = (
        db.query(Configuration)
        .filter(
            Configuration.id == config_id, Configuration.owner_id == current_user.id
        )
        .first()
    )

    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # If setting as default, unset other defaults
    if config_update.is_default:
        db.query(Configuration).filter(
            Configuration.owner_id == current_user.id,
            Configuration.is_default,
            Configuration.id != config_id,
        ).update({"is_default": False})

    # Update configuration
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)

    return config


@router.delete("/{config_id}")
def delete_configuration(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a configuration."""
    config = (
        db.query(Configuration)
        .filter(
            Configuration.id == config_id, Configuration.owner_id == current_user.id
        )
        .first()
    )

    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")

    db.delete(config)
    db.commit()

    return {"message": "Configuration deleted successfully"}
