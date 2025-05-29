import pandas as pd
from sqlalchemy import create_engine
from database_src import Session, engine, Base
from models import Parts
import pdb

images_csv_path = r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data_with_slicer_settings_parts_id.csv"

df_images = pd.read_csv(images_csv_path)
# Check if 'PartName' column exists
if "PartName" in df_images.columns:
    # Get unique part names
    unique_part_names = df_images["PartName"].unique()
    print("Unique part names:")
    for part_name in unique_part_names:
        print(f"- {part_name}")
else:
    print("Column 'PartName' not found in the DataFrame.")

session = Session()
# Iterate over the DataFrame rows to create Parts objects

for part_name in unique_part_names:

    # Create a new session

    # Check if the part already exists

    # Create a new Parts object
    part = Parts(
        name=part_name,
        url="not_documented",  # Assuming URL is not provided in the CSV, set it to None
        general_image=b"not_documented",  # Assuming general_image is not provided in the CSV, set it to None
    )

    # Add the object to the session
    session.add(part)

    # Commit the session to save the changes
    session.commit()

# Close the session
session.close()
