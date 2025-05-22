import json


def extract_relevant_slicing_parameters_from_string(content: str) -> dict:

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

    slicing_params = {}

    # Parameters to look for

    for line in content.split("\n"):
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

    return slicing_params
