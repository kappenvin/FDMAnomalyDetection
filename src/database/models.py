from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base


class ImageData(Base):
    __tablename__ = "image_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image: Mapped[bytes] = mapped_column(sa.LargeBinary)
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(), nullable=False, server_default=func.now()
    )
    slicer_settings_id: Mapped[int] = mapped_column(sa.ForeignKey("slicer_settings.id"))
    parts_id: Mapped[int] = mapped_column(sa.ForeignKey("parts.id"))
    label: Mapped[int]
    layer: Mapped[int]

    # Add relationships to Slicer_settings and Parts
    slicer_settings: Mapped[SlicerSettings] = relationship(back_populates="images")
    parts: Mapped[Parts] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, slicer_settings_id={self.slicer_settings_id}, parts_id={self.parts_id}, label={self.label}, layer={self.layer})>"


class SlicerSettings(Base):
    __tablename__ = "slicer_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sparse_infill_density: Mapped[int]
    sparse_infill_pattern: Mapped[str]
    sparse_infill_speed: Mapped[int]
    first_layer_bed_temperature: Mapped[int]
    bed_temperature_other_layers: Mapped[int]
    first_layer_nozzle_temperature: Mapped[int]
    nozzle_temperature_other_layers: Mapped[int]
    travel_speed: Mapped[int]
    first_layer_heigtht: Mapped[float]
    layer_height_other_layers: Mapped[float]
    line_width: Mapped[int]
    retraction_lenght: Mapped[float]
    filament_flow_ratio: Mapped[float]
    printer: Mapped[str]

    # add relationship to Image_data
    images: Mapped[list[ImageData]] = relationship(back_populates="slicer_settings")


# TODO : use alembic to change the columns


class Parts(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    url: Mapped[str]
    general_image: Mapped[bytes] = mapped_column(sa.LargeBinary)

    # add relationship to Image_data
    images: Mapped[list[ImageData]] = relationship(back_populates="parts")
