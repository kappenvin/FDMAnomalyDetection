from database import Session

# get_image.py
import os
from datetime import datetime

# Import your model
from models import ImageData  # Assuming models.py is in the same directory

# --- Optional: Create tables if they don't exist (for development) ---
# If your tables are already in the database, you can comment this out.
# Base.metadata.create_all(engine)
# -------------------------------------------------------------------


def get_image_from_db(image_id: int):
    """
    Fetches an image record from the database by its ID.
    Returns the ImageData object or None if not found.
    """
    session = Session()  # Get a new session
    try:
        # Query for the image by its primary key (id)
        image_record = session.query(ImageData).filter(ImageData.id == image_id).first()
        return image_record
    except Exception as e:
        print(f"Error fetching image with ID {image_id}: {e}")
        return None
    finally:
        session.close()  # Always close the session


def save_binary_data_to_file(binary_data: bytes, filename: str):
    """
    Saves binary data to a file.
    """
    if binary_data:
        try:
            with open(filename, "wb") as f:  # 'wb' for write binary
                f.write(binary_data)
            print(f"Binary data successfully saved to: {filename}")
        except IOError as e:
            print(f"Error saving file {filename}: {e}")
    else:
        print(f"No binary data provided to save to {filename}.")


if __name__ == "__main__":
    # --- Configuration ---
    # Replace with the ID of the image you want to retrieve
    target_image_id = 86261

    # Desired output filename (e.g., based on the original image type)
    # If your images are JPGs, use .jpg; if PNGs, use .png, etc.
    output_filename = f"retrieved_image_{target_image_id}.jpg"
    # -------------------

    print(f"Attempting to retrieve image with ID: {target_image_id}...")
    image_data_record = get_image_from_db(target_image_id)

    if image_data_record:
        print(f"\nSuccessfully retrieved record:")
        print(f"  ID: {image_data_record.id}")
        print(f"  Timestamp: {image_data_record.timestamp}")
        print(f"  Label: {image_data_record.label}")
        print(f"  Layer: {image_data_record.layer}")
        # Note: image_data_record.image will be the raw bytes

        if image_data_record.image:
            print(
                f"  Image data is present (size: {len(image_data_record.image)} bytes)."
            )
            save_binary_data_to_file(image_data_record.image, output_filename)
        else:
            print(f"  Image data for ID {target_image_id} is NULL in the database.")
    else:
        print(f"\nNo image record found with ID {target_image_id}.")
