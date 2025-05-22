import pandas as pd
from sqlalchemy import create_engine
from database import Session, engine, Base
from models import ImageData
import pdb
import sys

images_csv_path = r"C:\Anomaly_detection_3D_printing\data\csv_files\final_data_with_slicer_settings_parts_id.csv"

df_images = pd.read_csv(images_csv_path)

# Create a new SQLAlchemy session
session = Session()

for idx, row in df_images.iterrows():

    with open(row["ImageFilePath"], "rb") as f:
        image_bytes = f.read()

    # Create a new ImageData object
    image_data = ImageData(
        image=image_bytes,
        timestamp=row["Timestamp"],
        slicer_settings_id=row["slicer_settings_id"],
        parts_id=row["parts_id"],
        label=row["Class"],
        layer=row["LayerInfo"],
    )

    # Add the object to the session
    session.add(image_data)

    # Commit the session to save the changes
    session.commit()

    # Close the session
session.close()


print(f"finished reading csv file {images_csv_path}")
