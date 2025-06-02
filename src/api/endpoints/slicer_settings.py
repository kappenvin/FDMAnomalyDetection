"""
API endpoints for managing slicer settings.

This module contains all the REST endpoints for CRUD operations on slicer settings.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import sys
import os

# Add the database_src directory to the path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../../../data_processing/database_src")
)

from models import SlicerSettings
from ..core.database import get_db
from ..schemas import SlicerSettingsCreate, SlicerSettingsUpdate, SlicerSettingsResponse

router = APIRouter()


@router.get("/", response_model=List[SlicerSettingsResponse])
async def get_slicer_settings(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    printer_name: Optional[str] = Query(None, description="Filter by printer name"),
    slicer_profile: Optional[str] = Query(None, description="Filter by slicer profile"),
    db: Session = Depends(get_db),
):
    """
    Retrieve slicer settings with optional filtering.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        printer_name: Filter by printer name.
        slicer_profile: Filter by slicer profile.
        db: Database session.

    Returns:
        List of SlicerSettingsResponse objects.
    """
    try:
        query = db.query(SlicerSettings)

        # Apply filters
        if printer_name:
            query = query.filter(SlicerSettings.printer_name.ilike(f"%{printer_name}%"))
        if slicer_profile:
            query = query.filter(
                SlicerSettings.slicer_profile.ilike(f"%{slicer_profile}%")
            )

        # Apply pagination
        settings = query.offset(skip).limit(limit).all()

        return [SlicerSettingsResponse.from_orm(setting) for setting in settings]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving slicer settings: {str(e)}",
        )


@router.get("/{setting_id}", response_model=SlicerSettingsResponse)
async def get_slicer_setting(setting_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific slicer setting by ID.

    Args:
        setting_id: ID of the slicer setting to retrieve.
        db: Database session.

    Returns:
        SlicerSettingsResponse.
    """
    try:
        setting = (
            db.query(SlicerSettings).filter(SlicerSettings.id == setting_id).first()
        )
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Slicer setting with ID {setting_id} not found",
            )

        return SlicerSettingsResponse.from_orm(setting)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving slicer setting: {str(e)}",
        )


@router.post(
    "/", response_model=SlicerSettingsResponse, status_code=status.HTTP_201_CREATED
)
async def create_slicer_setting(
    setting_data: SlicerSettingsCreate, db: Session = Depends(get_db)
):
    """
    Create a new slicer setting record.

    Args:
        setting_data: Slicer setting data to create.
        db: Database session.

    Returns:
        Created SlicerSettingsResponse.
    """
    try:
        # Create new SlicerSettings object
        db_setting = SlicerSettings(**setting_data.dict())

        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)

        return SlicerSettingsResponse.from_orm(db_setting)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating slicer setting: {str(e)}",
        )


@router.put("/{setting_id}", response_model=SlicerSettingsResponse)
async def update_slicer_setting(
    setting_id: int, setting_update: SlicerSettingsUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing slicer setting record.

    Args:
        setting_id: ID of the slicer setting to update.
        setting_update: Updated slicer setting data.
        db: Database session.

    Returns:
        Updated SlicerSettingsResponse.
    """
    try:
        db_setting = (
            db.query(SlicerSettings).filter(SlicerSettings.id == setting_id).first()
        )
        if not db_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Slicer setting with ID {setting_id} not found",
            )

        # Update fields if provided
        update_data = setting_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_setting, field, value)

        db.commit()
        db.refresh(db_setting)

        return SlicerSettingsResponse.from_orm(db_setting)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating slicer setting: {str(e)}",
        )


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slicer_setting(setting_id: int, db: Session = Depends(get_db)):
    """
    Delete a slicer setting record.

    Args:
        setting_id: ID of the slicer setting to delete.
        db: Database session.
    """
    try:
        db_setting = (
            db.query(SlicerSettings).filter(SlicerSettings.id == setting_id).first()
        )
        if not db_setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Slicer setting with ID {setting_id} not found",
            )

        db.delete(db_setting)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting slicer setting: {str(e)}",
        )
