import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from database import Base, engine
from models import SlicerSettings
import pdb

# Load environment variables from .env file
load_dotenv(r"C:\Anomaly_detection_3D_printing\.env.database")

# Path to your CSV file
CSV_FILE_PATH = (
    r"C:\Anomaly_detection_3D_printing\data\csv_files\filtered_slicer_settings.csv"
)

# Name of the table in your PostgreSQL database
TABLE_NAME = "slicer_settings"

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)


def upload_dataframe_to_postgresql(df, table_name, engine, if_exists="append"):
    """
    Uploads a pandas DataFrame directly to a PostgreSQL table.

    Args:
        df (pandas.DataFrame): DataFrame to upload.
        table_name (str): Name of the table in the database.
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine object.
        if_exists (str): How to behave if the table already exists.
                         Options: 'fail', 'replace', 'append'. Default is 'replace'.
    """
    try:
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        print(f"Data uploaded to '{table_name}' successfully.")
    except Exception as e:
        print(f"Error uploading data to table '{table_name}': {e}")


if __name__ == "__main__":
    print
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"CSV data preview:\n{df.head()}")
        # Drop the 'difference_to' column if it exists
        print(df.columns)
        df = df.drop("difference_to", axis=1)
        print(df.columns)

        # Create database engine

        if engine:
            # Upload the DataFrame to PostgreSQL
            upload_dataframe_to_postgresql(
                df, TABLE_NAME, engine=engine, if_exists="append"
            )
    except FileNotFoundError:
        print(f"Error: Excel file not found at '{CSV_FILE_PATH}'")
    except Exception as e:
        print(f"Unexpected error: {e}")
