"""
API endpoints for managing image data.

This module contains all the REST endpoints for CRUD operations on image data.
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

from models import ImageData
from crud import get_image_data_by_column_value, delete_image_data_by_id
from ..core.database import get_db
from ..schemas import (
    ImageDataCreate,
    ImageDataUpdate,
    ImageDataResponse,
    ImageDataWithImageResponse,
    PaginationParams,
    ErrorResponse,
)

router = APIRouter()


@router.get("/", response_model=List[ImageDataResponse])
async def get_images(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    slicer_settings_id: Optional[int] = Query(
        None, description="Filter by slicer settings ID"
    ),
    parts_id: Optional[int] = Query(None, description="Filter by parts ID"),
    label: Optional[int] = Query(None, description="Filter by label"),
    layer: Optional[int] = Query(None, description="Filter by layer"),
    db: Session = Depends(get_db),
):
    """
    Retrieve image data with optional filtering.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        slicer_settings_id: Filter by slicer settings ID.
        parts_id: Filter by parts ID.
        label: Filter by label.
        layer: Filter by layer.
        db: Database session.

    Returns:
        List of ImageDataResponse objects.
    """
    try:
        query = db.query(ImageData)

        # Apply filters
        if slicer_settings_id is not None:
            query = query.filter(ImageData.slicer_settings_id == slicer_settings_id)
        if parts_id is not None:
            query = query.filter(ImageData.parts_id == parts_id)
        if label is not None:
            query = query.filter(ImageData.label == label)
        if layer is not None:
            query = query.filter(ImageData.layer == layer)

        # Apply pagination
        images = query.offset(skip).limit(limit).all()

        # Convert to response format without full image data
        return [ImageDataResponse.from_orm_with_image_size(img) for img in images]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving images: {str(e)}",
        )


@router.get("/{image_id}", response_model=ImageDataResponse)
async def get_image(
    image_id: int,
    include_image: bool = Query(False, description="Include base64 encoded image data"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific image by ID.

    Args:
        image_id: ID of the image to retrieve.
        include_image: Whether to include the base64 encoded image data.
        db: Database session.

    Returns:
        ImageDataResponse or ImageDataWithImageResponse.
    """
    try:
        image = db.query(ImageData).filter(ImageData.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found",
            )

        if include_image:
            return ImageDataWithImageResponse.from_orm_with_base64(image)
        else:
            return ImageDataResponse.from_orm_with_image_size(image)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving image: {str(e)}",
        )


@router.post("/", response_model=ImageDataResponse, status_code=status.HTTP_201_CREATED)
async def create_image(image_data: ImageDataCreate, db: Session = Depends(get_db)):
    """
    Create a new image record.

    Args:
        image_data: Image data to create.
        db: Database session.

    Returns:
        Created ImageDataResponse.
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.image)

        # Create new ImageData object
        db_image = ImageData(
            image=image_bytes,
            slicer_settings_id=image_data.slicer_settings_id,
            parts_id=image_data.parts_id,
            label=image_data.label,
            layer=image_data.layer,
        )

        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return ImageDataResponse.from_orm_with_image_size(db_image)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating image: {str(e)}",
        )


@router.put("/{image_id}", response_model=ImageDataResponse)
async def update_image(
    image_id: int, image_update: ImageDataUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing image record.

    Args:
        image_id: ID of the image to update.
        image_update: Updated image data.
        db: Database session.

    Returns:
        Updated ImageDataResponse.
    """
    try:
        db_image = db.query(ImageData).filter(ImageData.id == image_id).first()
        if not db_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found",
            )

        # Update fields if provided
        update_data = image_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_image, field, value)

        db.commit()
        db.refresh(db_image)

        return ImageDataResponse.from_orm_with_image_size(db_image)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating image: {str(e)}",
        )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """
    Delete an image record.

    Args:
        image_id: ID of the image to delete.
        db: Database session.
    """
    try:
        success = delete_image_data_by_id(db, image_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with ID {image_id} not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}",
        )


@router.get("/by-column/{column_name}", response_model=List[ImageDataResponse])
async def get_images_by_column(
    column_name: str, value: int, db: Session = Depends(get_db)
):
    """
    Get images filtered by a specific column value.

    Args:
        column_name: Name of the column to filter by.
        value: Value to filter for.
        db: Database session.

    Returns:
        List of ImageDataResponse objects.
    """
    try:
        images = get_image_data_by_column_value(db, column_name, value)
        return [ImageDataResponse.from_orm_with_image_size(img) for img in images]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving images by {column_name}: {str(e)}",
        )
