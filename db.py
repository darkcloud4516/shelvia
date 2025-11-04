from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.environ.get("SHELVIA_DATABASE_URL", "sqlite:///./defects.db")
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
