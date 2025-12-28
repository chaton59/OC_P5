from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True)
    features_json = Column(JSON)  # Features from sondage, eval, sirh data
    target = Column(String)  # Target: 'Oui' or 'Non' for turnover


class MLLog(Base):
    __tablename__ = "ml_logs"
    id = Column(Integer, primary_key=True)
    input_json = Column(JSON)  # Inputs flexibles (JSON for features variables)
    prediction = Column(String)  # Output ML ('Oui' or 'Non')
    created_at = Column(DateTime, default=func.now())  # Timestamp auto pour traçabilité
