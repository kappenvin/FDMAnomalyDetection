"""
Pydantic schemas for request/response models.

This module defines all the Pydantic models used for API request validation
and response serialization.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import base64


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        """Pydantic configuration."""

        orm_mode = True
        use_enum_values = True


# Image Data Schemas
class ImageDataBase(BaseSchema):
    """Base schema for ImageData."""

    slicer_settings_id: Optional[int] = None
    parts_id: Optional[int] = None
    label: Optional[int] = None
    layer: Optional[int] = None


class ImageDataCreate(ImageDataBase):
    """Schema for creating new ImageData."""

    image: str = Field(..., description="Base64 encoded image data")

    @validator("image")
    def validate_image_base64(cls, v):
        """Validate that the image is valid base64."""
        try:
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Invalid base64 image data")


class ImageDataUpdate(BaseSchema):
    """Schema for updating ImageData."""

    slicer_settings_id: Optional[int] = None
    parts_id: Optional[int] = None
    label: Optional[int] = None
    layer: Optional[int] = None


class ImageDataResponse(ImageDataBase):
    """Schema for ImageData response."""

    id: int
    timestamp: datetime
    image_size: Optional[int] = Field(None, description="Size of image in bytes")

    @classmethod
    def from_orm_with_image_size(cls, obj):
        """Create response with image size instead of full image data."""
        data = {
            "id": obj.id,
            "timestamp": obj.timestamp,
            "slicer_settings_id": obj.slicer_settings_id,
            "parts_id": obj.parts_id,
            "label": obj.label,
            "layer": obj.layer,
            "image_size": len(obj.image) if obj.image else None,
        }
        return cls(**data)


class ImageDataWithImageResponse(ImageDataResponse):
    """Schema for ImageData response including base64 image."""

    image: str = Field(..., description="Base64 encoded image data")

    @classmethod
    def from_orm_with_base64(cls, obj):
        """Create response with base64 encoded image."""
        data = {
            "id": obj.id,
            "timestamp": obj.timestamp,
            "slicer_settings_id": obj.slicer_settings_id,
            "parts_id": obj.parts_id,
            "label": obj.label,
            "layer": obj.layer,
            "image_size": len(obj.image) if obj.image else None,
            "image": base64.b64encode(obj.image).decode("utf-8") if obj.image else "",
        }
        return cls(**data)


# Slicer Settings Schemas
class SlicerSettingsBase(BaseSchema):
    """Base schema for SlicerSettings."""

    slicer_profile: str
    sparse_infill_density: int
    sparse_infill_pattern: str
    sparse_infill_speed: int
    first_layer_bed_temperature: int
    bed_temperature_other_layers: int
    first_layer_nozzle_temperature: int
    nozzle_temperature_other_layers: int
    travel_speed: int
    first_layer_height: float
    layer_height_other_layers: float
    line_width: float
    retraction_length: float
    filament_flow_ratio: float
    printer_name: str


class SlicerSettingsCreate(SlicerSettingsBase):
    """Schema for creating new SlicerSettings."""

    pass


class SlicerSettingsUpdate(BaseSchema):
    """Schema for updating SlicerSettings."""

    slicer_profile: Optional[str] = None
    sparse_infill_density: Optional[int] = None
    sparse_infill_pattern: Optional[str] = None
    sparse_infill_speed: Optional[int] = None
    first_layer_bed_temperature: Optional[int] = None
    bed_temperature_other_layers: Optional[int] = None
    first_layer_nozzle_temperature: Optional[int] = None
    nozzle_temperature_other_layers: Optional[int] = None
    travel_speed: Optional[int] = None
    first_layer_height: Optional[float] = None
    layer_height_other_layers: Optional[float] = None
    line_width: Optional[float] = None
    retraction_length: Optional[float] = None
    filament_flow_ratio: Optional[float] = None
    printer_name: Optional[str] = None


class SlicerSettingsResponse(SlicerSettingsBase):
    """Schema for SlicerSettings response."""

    id: int


# Parts Schemas
class PartsBase(BaseSchema):
    """Base schema for Parts."""

    name: str
    url: str


class PartsCreate(PartsBase):
    """Schema for creating new Parts."""

    general_image: str = Field(..., description="Base64 encoded image data")

    @validator("general_image")
    def validate_image_base64(cls, v):
        """Validate that the image is valid base64."""
        try:
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Invalid base64 image data")


class PartsUpdate(BaseSchema):
    """Schema for updating Parts."""

    name: Optional[str] = None
    url: Optional[str] = None
    general_image: Optional[str] = None

    @validator("general_image")
    def validate_image_base64(cls, v):
        """Validate that the image is valid base64."""
        if v is not None:
            try:
                base64.b64decode(v)
                return v
            except Exception:
                raise ValueError("Invalid base64 image data")
        return v


class PartsResponse(PartsBase):
    """Schema for Parts response."""

    id: int
    image_size: Optional[int] = Field(
        None, description="Size of general image in bytes"
    )

    @classmethod
    def from_orm_with_image_size(cls, obj):
        """Create response with image size instead of full image data."""
        data = {
            "id": obj.id,
            "name": obj.name,
            "url": obj.url,
            "image_size": len(obj.general_image) if obj.general_image else None,
        }
        return cls(**data)


class PartsWithImageResponse(PartsResponse):
    """Schema for Parts response including base64 image."""

    general_image: str = Field(..., description="Base64 encoded image data")

    @classmethod
    def from_orm_with_base64(cls, obj):
        """Create response with base64 encoded image."""
        data = {
            "id": obj.id,
            "name": obj.name,
            "url": obj.url,
            "image_size": len(obj.general_image) if obj.general_image else None,
            "general_image": (
                base64.b64encode(obj.general_image).decode("utf-8")
                if obj.general_image
                else ""
            ),
        }
        return cls(**data)


# Inference Schemas
class InferenceRequest(BaseSchema):
    """Schema for anomaly detection inference request."""

    image: str = Field(..., description="Base64 encoded image data")
    model_type: str = Field(
        default="standard", description="Model type: 'standard' or 'quantized'"
    )

    @validator("image")
    def validate_image_base64(cls, v):
        """Validate that the image is valid base64."""
        try:
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Invalid base64 image data")

    @validator("model_type")
    def validate_model_type(cls, v):
        """Validate model type."""
        if v not in ["standard", "quantized"]:
            raise ValueError('model_type must be either "standard" or "quantized"')
        return v


class InferenceResponse(BaseSchema):
    """Schema for anomaly detection inference response."""

    prediction: float = Field(..., description="Anomaly probability (0.0 to 1.0)")
    is_anomaly: bool = Field(
        ..., description="Whether the image is classified as anomalous"
    )
    confidence: float = Field(..., description="Confidence score")
    model_used: str = Field(..., description="Model type used for inference")
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds"
    )


# Pagination Schema
class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of records to return"
    )


# Error Response Schema
class ErrorResponse(BaseSchema):
    """Schema for error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
