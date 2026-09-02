from fastapi import HTTPException
from sqlalchemy.orm import Session
from auth import verifier_pin_hashe
import models


def deduire_solde(db: Session, utilisateur_id: int, montant: float):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.id == utilisateur_id).with_for_update().first()
    if utilisateur.solde < montant:
        raise HTTPException(status_code=400, detail="Solde insuffisant")
    utilisateur.solde -= montant
    return utilisateur.solde


def ajouter_solde(db: Session, utilisateur_id: int, montant: float):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.id == utilisateur_id).with_for_update().first()
    utilisateur.solde += montant
    return utilisateur.solde


def creer_transaction(db: Session, type: str, montant: float, utilisateur_id: int, autre_utilisateur_id: int, solde_apres: float):
    transaction = models.Transaction(
        type=type,
        montant=montant,
        utilisateur_id=utilisateur_id,
        autre_utilisateur_id=autre_utilisateur_id,
        solde_apres=solde_apres
    )
    db.add(transaction)
    return transaction



def verifier_pin_utilisateur(utilisateur, pin_tape: str, db: Session):
    if utilisateur.compte_bloque:
        raise HTTPException(status_code=403, detail="Compte bloqué, contactez un admin")

    if not verifier_pin_hashe(pin_tape, utilisateur.code_pin):
        utilisateur.tentatives_pin_echouees += 1
        if utilisateur.tentatives_pin_echouees >= 3:
            utilisateur.compte_bloque = True
        db.commit()
        raise HTTPException(status_code=401, detail="Code PIN incorrect")

    utilisateur.tentatives_pin_echouees = 0
    db.commit()
    return True