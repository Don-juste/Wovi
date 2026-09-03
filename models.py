from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    telephone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    mot_de_passe = Column(String)
    fcm_token = Column(String, nullable=True)
    code_pin = Column(String)
    solde = Column(Float, default=0.0)
    otp_code = Column(String, nullable=True)
    otp_expiration = Column(DateTime, nullable=True)
    tentatives_pin_echouees = Column(Integer, default=0)
    compte_bloque = Column(Boolean, default=False)

    transactions = relationship("Transaction", foreign_keys="Transaction.utilisateur_id", back_populates="utilisateur")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    montant = Column(Float)
    date = Column(DateTime, default=func.now())
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    autre_utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    solde_apres = Column(Float)

    utilisateur = relationship("Utilisateur", foreign_keys=[utilisateur_id], back_populates="transactions")
    autre_utilisateur = relationship("Utilisateur", foreign_keys=[autre_utilisateur_id])


class LogConnexion(Base):
    __tablename__ = "logs_connexion"
    id = Column(Integer, primary_key=True, index=True)
    telephone = Column(String)
    date = Column(DateTime, default=func.now())
    succes = Column(Boolean)
    adresse_ip = Column(String, nullable=True)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    email = Column(String, unique=True, index=True)
    mot_de_passe = Column(String)