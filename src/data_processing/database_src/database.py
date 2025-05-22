import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection details from environment variables
db_user = os.getenv("DB_USER", "postgres")  # Default if not found
db_password = os.getenv("DB_PASSWORD", "")  # Default if not found
db_host = os.getenv("DB_HOST", "localhost")  # Default if not found
db_port = os.getenv("DB_PORT", "5431")  # Default if not found

# Construct the connection string
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}"

# Create SQLAlchemy engine and session factory
engine = sa.create_engine(db_url)
Session = sessionmaker(bind=engine)

# Create the base class for declarative models
Base = declarative_base()
