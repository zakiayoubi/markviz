# Database models

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# create the SQLAlchemy engine
# it connects to the postgres database and handles openning and closing the
# connections effeciently.
engine = create_engine(DATABASE_URL)

# Create a session factory
# a session is like a temporary workspace where you make changes to the
# database like adding, updating, deleting, etc to the database
# SessionLocal() gives you a new session whenever you need one.
# We always close it after use (that's why we have the try/finally in get_db).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()


# Dependency to get DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
