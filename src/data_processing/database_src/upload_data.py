from .models import Parts, ImageData, SlicerSettings
from .database import Session, engine, Base

def upload_image_db(image_bytes, timestamp, slicer_settings_id, parts_id, label, layer):

    session = Session()
    """
    Uploads image data to the database.

    Args:
        image_bytes: The image data in bytes.
        timestamp: The timestamp of the image.
        slicer_settings_id: The ID of the slicer settings.
        parts_id: The ID of the part.
        label: The label for the image.
        layer: The layer information.

    Returns:
        None
    """
    session = Session()
    try:
        image_data = ImageData(
            image=image_bytes,
            timestamp=timestamp,
            slicer_settings_id=slicer_settings_id,
            parts_id=parts_id,
            label=label,
            layer=layer
        )
        session.add(image_data)
        session.commit()
    except Exception as e:
        print(f"Error uploading image data: {e}")
        session.rollback()
    finally:
        session.close()

def upload_slicer_settings_db(params):

    session = Session()
    # Prepare data for SlicerSettings, ensuring correct types
    try:
        slicer_profile_val = "to_delete"  # Or derive from params if available
        sparse_infill_density_val = int(params["sparse_infill_density"][:-1])
        sparse_infill_pattern_val = params["sparse_infill_pattern"]
        sparse_infill_speed_val = int(params["sparse_infill_speed"])
        first_layer_bed_temp_val = int(params["first_layer_bed_temperature"])
        # Assuming bed_temperature_other_layers is same as first layer for this logic
        bed_temp_other_layers_val = int(params["first_layer_bed_temperature"])
        first_layer_nozzle_temp_val = int(params["nozzle_temperature_initial_layer"])
        nozzle_temp_other_layers_val = int(params["nozzle_temperature"])
        travel_speed_val = int(params["travel_speed"])
        first_layer_height_val = float(params["first_layer_height"])
        layer_height_other_layers_val = float(params["layer_height"])
        line_width_val = float(
            params["line_width"][:-1]
        )  # Assuming it's a percentage to be converted
        retraction_length_val = float(params["retraction_length"])
        filament_flow_ratio_val = float(params["filament_flow_ratio"])
        printer_name_val = "SovolSv06"  # Or derive from params if available
    except Exception as e:
        print(f"Error uploading part data: {e}")
        session.close()
        return None

    # Check if a SlicerSettings record with these parameters already exists
    existing_setting = (
        session.query(SlicerSettings)
        .filter_by(
            slicer_profile=slicer_profile_val,
            sparse_infill_density=sparse_infill_density_val,
            sparse_infill_pattern=sparse_infill_pattern_val,
            sparse_infill_speed=sparse_infill_speed_val,
            first_layer_bed_temperature=first_layer_bed_temp_val,
            bed_temperature_other_layers=bed_temp_other_layers_val,
            first_layer_nozzle_temperature=first_layer_nozzle_temp_val,
            nozzle_temperature_other_layers=nozzle_temp_other_layers_val,
            travel_speed=travel_speed_val,
            first_layer_height=first_layer_height_val,
            layer_height_other_layers=layer_height_other_layers_val,
            line_width=line_width_val,
            retraction_length=retraction_length_val,
            filament_flow_ratio=filament_flow_ratio_val,
            printer_name=printer_name_val,
        )
        .first()
    )

    if existing_setting:
        print(
            f"Slicer settings already exist with ID: {existing_setting.id}. Skipping add."
        )
        slicer_setting_id = existing_setting.id
    else:
        print("No existing slicer settings found. Adding new record.")
        slicer_setting = SlicerSettings(
            slicer_profile=slicer_profile_val,
            sparse_infill_density=sparse_infill_density_val,
            sparse_infill_pattern=sparse_infill_pattern_val,
            sparse_infill_speed=sparse_infill_speed_val,
            first_layer_bed_temperature=first_layer_bed_temp_val,
            bed_temperature_other_layers=bed_temp_other_layers_val,
            first_layer_nozzle_temperature=first_layer_nozzle_temp_val,
            nozzle_temperature_other_layers=nozzle_temp_other_layers_val,
            travel_speed=travel_speed_val,
            first_layer_height=first_layer_height_val,
            layer_height_other_layers=layer_height_other_layers_val,
            line_width=line_width_val,
            retraction_length=retraction_length_val,
            filament_flow_ratio=filament_flow_ratio_val,
            printer_name=printer_name_val,
        )
        session.add(slicer_setting)
        session.commit()
        print(f"New slicer settings added with ID: {slicer_setting.id}.")
        slicer_setting_id = slicer_setting.id


    session.close()
    return slicer_setting_id

def upload_part_db(part_name, url=None, general_image=None):
    """
    Uploads part data to the database.

    Args:
        part_name: The name of the part.
        url: The URL of the part (optional).
        general_image: The general image of the part (optional).

    Returns:
        None
    """
    session = Session()
    try:
        existing_part = (
            session.query(Parts)
            .filter_by(
                name=part_name,
                url=url if url else "not_documented",
                general_image=general_image if general_image else b"not_documented"
            )
            .first()
        )

        if existing_part:
            print(f"Part already exists with ID: {existing_part.id}. Skipping add.")
            part_id = existing_part.id
        else:
            part = Parts(
                name=part_name,
            url=url if url else "not_documented",
            general_image=general_image if general_image else b"not_documented"
            )
            session.add(part)
            session.commit()
            part_id = part.id
    except Exception as e:
        print(f"Error uploading part data: {e}")
        session.close()
    finally:
        session.close()
    return part_id