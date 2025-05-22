from sqlalchemy.orm import Session
from models import ImageData


def get_image_data_by_column_value(session, column_name, value):
    """
    Retrieves all image data rows where the specified column matches the given value.

    Args:
        session: SQLAlchemy session object.
        column_name: The name of the column to filter by (e.g., "layer", "slicer_settings_id").
        value: The value to filter for.

    Returns:
        list: List of Image_data objects matching the criteria.
    """
    try:
        # Check if the column exists in the Image_data model
        if not hasattr(ImageData, column_name):
            print(f"Error: Column '{column_name}' does not exist in Image_data model")
            return []

        # Build and execute the query
        query = session.query(ImageData).filter(
            getattr(ImageData, column_name) == value
        )
        results = query.all()

        return results

    except Exception as e:
        print(f"Error querying image data by {column_name}: {e}")
        return []


def delete_image_data_by_id(session, image_id):
    """
    Deletes an Image_data row by its ID.

    Args:
        session: SQLAlchemy session object.
        image_id: The ID of the row to delete.

    Returns:
        True if the row was deleted, False if not found.
    """
    row_to_delete = session.query(ImageData).filter_by(id=image_id).first()
    if row_to_delete:
        session.delete(row_to_delete)
        session.commit()
        return True
    else:
        return False
