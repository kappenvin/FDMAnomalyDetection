import sqlalchemy as sa
from database import db


def drop_column_from_table(column_name: str, table_name: str = "image_data"):
    """
    Drops a column from a database table using raw SQL.

    Args:
        column_name: The name of the column to drop.
        table_name: The name of the table (default is 'image_data').

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with db.begin() as connection:
            # Check if column exists before attempting to drop it
            check_sql = sa.text(
                f"SELECT column_name FROM information_schema.columns "
                f"WHERE table_name = '{table_name}' AND column_name = '{column_name}'"
            )
            result = connection.execute(check_sql).scalar()

            if not result:
                print(f"Column '{column_name}' does not exist in table '{table_name}'.")
                return False

            # Drop the column
            drop_sql = sa.text(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
            connection.execute(drop_sql)
            print(
                f"Column '{column_name}' successfully dropped from table '{table_name}'."
            )
            return True

    except Exception as e:
        print(f"Error dropping column '{column_name}' from table '{table_name}': {e}")
        return False


def add_column_to_table(
    column_name: str, column_type: str, table_name: str = "image_data"
):
    """
    Adds a column to a database table using raw SQL.

    Args:
        column_name: The name of the column to add.
        column_type: The SQL data type of the column (e.g., 'INTEGER', 'TEXT').
        table_name: The name of the table (default is 'image_data').

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with db.begin() as connection:
            # Check if column already exists
            check_sql = sa.text(
                f"SELECT column_name FROM information_schema.columns "
                f"WHERE table_name = '{table_name}' AND column_name = '{column_name}'"
            )
            result = connection.execute(check_sql).scalar()

            if result:
                print(f"Column '{column_name}' already exists in table '{table_name}'.")
                return True

            # Add the column
            add_sql = sa.text(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )
            connection.execute(add_sql)
            print(f"Column '{column_name}' successfully added to table '{table_name}'.")
            return True

    except Exception as e:
        print(f"Error adding column '{column_name}' to table '{table_name}': {e}")
        return False
