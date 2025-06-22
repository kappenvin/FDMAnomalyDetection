from Klipper_class import KlipperPrinter
import pdb
import requests
import time
from gcode_extraction.extract_gcode_from_string import (
    extract_relevant_slicing_parameters_from_string,
)

from database_src.models import SlicerSettings
from database_src.database import Session
import sys

url = "http://192.168.2.170/"
printer = KlipperPrinter(url)
# start Session
session = Session()

printer_gcode_filename = printer.get("/printer/objects/query?print_stats")["result"][
    "status"
]["print_stats"]["filename"]
print(f"Current G-code file: {printer_gcode_filename}")


printer_gcode = (
    "schnappverbindung_kiste v9_0.2mm_PLA_Generic Klipper Printer_20m24_test.gcode"
)

gcode_download_url = f"/server/files/gcodes/{printer_gcode}"

gcode_response = printer.get_download(gcode_download_url)
print(gcode_response)
gcode_content = gcode_response.text

# extract the gcode parameters
params = extract_relevant_slicing_parameters_from_string(
    gcode_content,
)
print(params)

for key, value in params.items():
    print(f"{key}: {value} (type: {type(value)})")

sys.exit(0)  # Exit after extracting parameters for debugging

# Prepare data for SlicerSettings, ensuring correct types
try:
    slicer_profile_val = "to_delete_2"  # Or derive from params if available
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
except KeyError as e:
    print(f"Error: Missing key in extracted G-code parameters: {e}")
    session.close()
    exit()  # Or handle more gracefully
except ValueError as e:
    print(f"Error: Could not convert parameter to expected type: {e}")
    session.close()
    exit()  # Or handle more gracefully


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

print(f"Extracted parameters: {params}")
print(f"Using SlicerSetting ID: {slicer_setting_id}")
