import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create the SQLAlchemy engine. 
# We enable SQL echoing (echo=True) so you can see the actual SQL Alembic and SQLAlchemy execute in your console!
engine = create_engine(
    DATABASE_URL,
    echo=True, 
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for our models
Base = declarative_base()

# Dependency to yield database sessions per request in FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
