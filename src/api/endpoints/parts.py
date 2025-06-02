"""
API endpoints for managing parts.

This module contains all the REST endpoints for CRUD operations on parts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import base64
import sys
import os

# Add the database_src directory to the path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../../../data_processing/database_src")
)

from models import Parts
from ..core.database import get_db
from ..schemas import PartsCreate, PartsUpdate, PartsResponse, PartsWithImageResponse

router = APIRouter()


@router.get("/", response_model=List[PartsResponse])
async def get_parts(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    name: Optional[str] = Query(None, description="Filter by part name"),
    db: Session = Depends(get_db),
):
    """
    Retrieve parts with optional filtering.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        name: Filter by part name.
        db: Database session.

    Returns:
        List of PartsResponse objects.
    """
    try:
        query = db.query(Parts)

        # Apply filters
        if name:
            query = query.filter(Parts.name.ilike(f"%{name}%"))

        # Apply pagination
        parts = query.offset(skip).limit(limit).all()

        return [PartsResponse.from_orm_with_image_size(part) for part in parts]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving parts: {str(e)}",
        )


@router.get("/{part_id}", response_model=PartsResponse)
async def get_part(
    part_id: int,
    include_image: bool = Query(False, description="Include base64 encoded image data"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific part by ID.

    Args:
        part_id: ID of the part to retrieve.
        include_image: Whether to include the base64 encoded image data.
        db: Database session.

    Returns:
        PartsResponse or PartsWithImageResponse.
    """
    try:
        part = db.query(Parts).filter(Parts.id == part_id).first()
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Part with ID {part_id} not found",
            )

        if include_image:
            return PartsWithImageResponse.from_orm_with_base64(part)
        else:
            return PartsResponse.from_orm_with_image_size(part)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving part: {str(e)}",
        )


@router.post("/", response_model=PartsResponse, status_code=status.HTTP_201_CREATED)
async def create_part(part_data: PartsCreate, db: Session = Depends(get_db)):
    """
    Create a new part record.

    Args:
        part_data: Part data to create.
        db: Database session.

    Returns:
        Created PartsResponse.
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(part_data.general_image)

        # Create new Parts object
        db_part = Parts(
            name=part_data.name, url=part_data.url, general_image=image_bytes
        )

        db.add(db_part)
        db.commit()
        db.refresh(db_part)

        return PartsResponse.from_orm_with_image_size(db_part)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating part: {str(e)}",
        )


@router.put("/{part_id}", response_model=PartsResponse)
async def update_part(
    part_id: int, part_update: PartsUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing part record.

    Args:
        part_id: ID of the part to update.
        part_update: Updated part data.
        db: Database session.

    Returns:
        Updated PartsResponse.
    """
    try:
        db_part = db.query(Parts).filter(Parts.id == part_id).first()
        if not db_part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Part with ID {part_id} not found",
            )

        # Update fields if provided
        update_data = part_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "general_image" and value is not None:
                # Decode base64 image
                value = base64.b64decode(value)
            setattr(db_part, field, value)

        db.commit()
        db.refresh(db_part)

        return PartsResponse.from_orm_with_image_size(db_part)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating part: {str(e)}",
        )


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(part_id: int, db: Session = Depends(get_db)):
    """
    Delete a part record.

    Args:
        part_id: ID of the part to delete.
        db: Database session.
    """
    try:
        db_part = db.query(Parts).filter(Parts.id == part_id).first()
        if not db_part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Part with ID {part_id} not found",
            )

        db.delete(db_part)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting part: {str(e)}",
        )
