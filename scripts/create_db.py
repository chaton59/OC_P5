#!/usr/bin/env python3
"""
Script de création de la base de données et des tables via SQLAlchemy.

Ce script utilise SQLAlchemy pour créer automatiquement la base de données
et les tables nécessaires pour le projet Employee Turnover.
"""
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()
engine = create_engine("postgresql://ml_user:15975359320@localhost/oc_p5_db")


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True)
    features_json = Column(JSON)  # Toutes les caractéristiques du dataset
    target = Column(String)  # Label: 'Oui' ou 'Non' pour le turnover


class MLLog(Base):
    __tablename__ = "ml_logs"
    id = Column(Integer, primary_key=True)
    input_json = Column(JSON)  # Données d'entrée de la prédiction
    prediction = Column(String)  # Prédiction: 'Oui' ou 'Non'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Création de toutes les tables
Base.metadata.create_all(engine)

print("✅ Base de données et tables créées avec succès !")
print("📊 Tables créées :")
print("   - dataset : Stockage des données d'entraînement")
print("   - ml_logs : Logs des prédictions de l'API")
