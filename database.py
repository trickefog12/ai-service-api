import os
import secrets
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Για Cloud SQL μέσω Cloud Run χρειάζεται αυτό το arg μόνο για SQLite
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    stripe_id = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    api_key = Column(String, unique=True, index=True)
    amount = Column(Integer)
    status = Column(String)


def generate_api_key() -> str:
    return f"sk_{secrets.token_urlsafe(32)}"


Base.metadata.create_all(bind=engine)