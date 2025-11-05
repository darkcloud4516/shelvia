from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.environ.get("SHELVIA_DATABASE_URL", "sqlite:///./defects.db")
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    # ensure models are imported so SQLModel.metadata is populated
    import models
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
