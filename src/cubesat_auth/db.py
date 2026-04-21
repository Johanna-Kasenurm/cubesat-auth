from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from cubesat_auth.config import DB_PATH
from cubesat_auth.models import User, Session

# Define a connection string for the database
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Connection manager for the database
engine = create_engine(DATABASE_URL, echo=False, future=True) # disable SQL logging and use the latest SQLAlchemy features
# Create a session maker for the database
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) # don't auto-write changes and require explicit commit
# Create a base class for the database models
Base = declarative_base()


# Initialise the database
def init_db() -> None:
    Base.metadata.create_all(engine) # create all the tables in the database