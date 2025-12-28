from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Dataset(Base):
    __tablename__ = 'dataset'
    id = Column(Integer, primary_key=True)
    text = Column(String)  # Feature principale pour P4 (texte à classer)
    category = Column(String)  # Label/cible (e.g., 'spam' ou 'ham')
    # Si P3 : Ajoute e.g., energy_use = Column(Float), building_type = Column(String)

class MLLog(Base):
    __tablename__ = 'ml_logs'
    id = Column(Integer, primary_key=True)
    input_json = Column(JSON)  # Inputs flexibles (JSON pour features variables)
    prediction = Column(String)  # Output ML (String pour classification ; Float si régression)
    created_at = Column(DateTime, default=func.now())  # Timestamp auto pour traçabilité
