"""Create SQLAlchemy engine and session objects."""
from sqlalchemy import create_engine , event
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URI

    
# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, fast_executemany=True,connect_args={'connect_timeout': 1200})

# Create database session
Session = sessionmaker(bind=engine)
session_factory = Session()

from .models import *