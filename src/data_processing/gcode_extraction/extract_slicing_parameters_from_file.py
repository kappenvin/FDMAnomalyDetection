import json

# global variables
parameters = [
    "sparse_infill_density",
    "sparse_infill_pattern",
    "sparse_infill_speed",
    "first_layer_bed_temperature",
    "nozzle_temperature_initial_layer",
    "nozzle_temperature",
    "travel_speed",
    "retraction_length",
    "first_layer_height",
    "layer_height",
    "line_width",
    "filament_flow_ratio",
]


def extract_relevant_slicing_parameters_from_file(input_file_path, output_file_path):
    """
    Extracts only first_layer_temperature and infill_density from a G-code file.

    Args:
        input_file_path (str): The path to the G-code file.
        output_file_path (str): The path where to save the JSON output.

    Returns:
        dict: A dictionary containing only first_layer_temperature and infill_density.
    """
    slicing_params = {}
    parameters = [
        "sparse_infill_density",
        "sparse_infill_pattern",
        "sparse_infill_speed",
        "first_layer_bed_temperature",
        "nozzle_temperature_initial_layer",
        "nozzle_temperature",
        "travel_speed",
        "retraction_length",
        "first_layer_height",
        "layer_height",
        "line_width",
        "filament_flow_ratio",
    ]
    # Parameters to look for

    with open(input_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()
            if line.startswith(";"):  # Only process comment lines
                line = line.lstrip(";").strip()  # Remove semicolon and extra whitespace

                # Check each parameter
                for param in parameters:
                    # Create patterns to match the parameter followed by : or =
                    pattern_equal = f"{param} ="
                    if line.startswith(pattern_equal):
                        # print(f"Found parameter: {param} in line: {line}")
                        # Extract the value after '='
                        if "=" in line:
                            value = line.split("=")[1].strip()
                            # Remove the second value if it exists
                            if "," in value:
                                value = value.split(",")[0]

                        slicing_params[param] = value

                        # Break if we found all parameters
                        if len(slicing_params) == len(parameters):
                            break

    # Save the dictionary to a file
    with open(output_file_path, "w") as f:
        json.dump(slicing_params, f, indent=4)

    return slicing_params


# Example usage:
if __name__ == "__main__":
    input_file_path = (
        r"C:\Anomaly_detection_3D_printing\data\gcode\orcaslicer_gcode.gcode"
    )
    output_file_path = (
        r"C:\Anomaly_detection_3D_printing\data\gcode\test_gcode_output.json"
    )
    params = extract_relevant_slicing_parameters_from_file(
        input_file_path, output_file_path
    )
    # print(f"Extracted parameters: {params}")
    """
    if params:
        # print(len(params))
        # print(len(parameters))
        set_params = set(params.keys())
        set_parameters = set(parameters)
        values_not_in_params = set_parameters - set_params
        # print(f"Parameters not found in G-code: {values_not_in_params}")

    else:
        print("No parameters found.")
        """
