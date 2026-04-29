from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Δημιουργούμε το αρχείο της βάσης
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Ο πίνακας των πληρωμών μας
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    stripe_id = Column(String, unique=True, index=True) # Το ID της πληρωμής από το Stripe
    email = Column(String)
    amount = Column(Integer)
    status = Column(String) # π.χ. "completed"

# Δημιουργία των πινάκων
Base.metadata.create_all(bind=engine)