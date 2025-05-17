import pandas as pd
import pdb


images_csv = r"C:\Anomaly_detection_3D_printing\data\csv_files\corrected_final_data.csv"
slicer_settings_excel = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\filtered_slicer_settings.csv"
)


images = pd.read_csv(images_csv)
slicer_settings = pd.read_csv(slicer_settings_excel)
parts_name = images["PartName"].unique()
slicer_settings_name = slicer_settings["slicer_profile"].unique()

slicer_settings_dict = {name: i + 1 for i, name in enumerate(slicer_settings_name)}
print(slicer_settings_dict)

"""
settings_to_exclude = ["standard2", "slicer_settings_4"]
images_filtered = images[~images["SlicerSettings"].isin(settings_to_exclude)].copy()
"""
"""
settings_to_delete = [
    "stringing3",
    "lowerspeed 4 ",
    "lowerspeed 3",
    "overextrusion4",
    "underextrusion3",
    "underextrusion1",
    "underextrusion2",
]
slicer_settings_filtered = slicer_settings[
    ~slicer_settings["slicer_profile"].isin(settings_to_delete)
].copy()

new_csv_path = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\filtered_slicer_settings.csv"
)
slicer_settings_filtered.to_csv(new_csv_path, index=False)


unique_slicer_settings_in_images = images_filtered["SlicerSettings"].unique()

# Convert the unique settings from the DataFrame column into a set
set_of_image_settings = set(unique_slicer_settings_in_images)

# Get the keys from the slicer_settings_dict and convert them into a set
set_of_dict_keys = set(slicer_settings_dict.keys())

# Find the settings that are in the images DataFrame but NOT in the slicer_settings_dict
settings_not_in_dict = set_of_image_settings - set_of_dict_keys
settings_not_in_images = set_of_dict_keys - set_of_image_settings
print(f"Settings in dict not in images: {settings_not_in_images}")
print(f"Settings in images not in dict: {settings_not_in_dict}")

# new _csv files
path_images = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\corrected_final_data.csv"
)
images_filtered.to_csv(path_images, index=False)
"""

pdb.set_trace()

images["slicer_settings_id"] = images["SlicerSettings"].map(slicer_settings_dict)
images["slicer_settings_id"] = images["slicer_settings_id"].astype(int)
new_images_csv = r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data_with_slicer_settings_id.csv"
images.to_csv(new_images_csv, index=False)
