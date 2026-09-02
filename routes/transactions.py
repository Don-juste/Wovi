from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependances import get_db, get_current_utilisateur
import models
import shemas
from calculs import deduire_solde, ajouter_solde, creer_transaction, verifier_pin_utilisateur
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/utilisateur/depot")
def depot(data: shemas.DepotRequest, current_utilisateur=Depends(get_current_utilisateur), db: Session = Depends(get_db)):
    verifier_pin_utilisateur(current_utilisateur, data.code_pin, db)

    nouveau_solde = ajouter_solde(db, current_utilisateur.id, data.montant)
    creer_transaction(db, "depot", data.montant, current_utilisateur.id, None, nouveau_solde)

    db.commit()

    logger.info(f"Dépôt effectué : {current_utilisateur.telephone}, montant : {data.montant}")

    return {"Message": "Dépôt effectué avec succès", "nouveau_solde": nouveau_solde}

@router.post("/utilisateur/retrait")
def retrait(data: shemas.RetraitRequest, current_utilisateur=Depends(get_current_utilisateur), db: Session = Depends(get_db)):
    verifier_pin_utilisateur(current_utilisateur, data.code_pin, db)

    nouveau_solde = deduire_solde(db, current_utilisateur.id, data.montant)
    creer_transaction(db, "retrait", data.montant, current_utilisateur.id, None, nouveau_solde)

    db.commit()

    logger.info(f"Retrait effectué : {current_utilisateur.telephone}, montant : {data.montant}")

    return {"Message": "Retrait effectué avec succès", "nouveau_solde": nouveau_solde}

@router.post("/utilisateur/transfert")
def transfert(data: shemas.TransfertRequest, current_utilisateur=Depends(get_current_utilisateur), db: Session = Depends(get_db)):
    verifier_pin_utilisateur(current_utilisateur, data.code_pin, db)

    destinataire = db.query(models.Utilisateur).filter(models.Utilisateur.telephone == data.telephone_destinataire).first()
    if destinataire is None:
        raise HTTPException(status_code=404, detail="Ce numéro n'existe pas dans notre système")

    if destinataire.id == current_utilisateur.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous transférer de l'argent à vous-même")

    solde_expediteur = deduire_solde(db, current_utilisateur.id, data.montant)
    creer_transaction(db, "transfert_sortant", data.montant, current_utilisateur.id, destinataire.id, solde_expediteur)

    solde_destinataire = ajouter_solde(db, destinataire.id, data.montant)
    creer_transaction(db, "transfert_entrant", data.montant, destinataire.id, current_utilisateur.id, solde_destinataire)

    db.commit()

    logger.info(f"Transfert effectué : {current_utilisateur.telephone} → {destinataire.telephone}, montant : {data.montant}")

    return {"Message": "Transfert effectué avec succès", "nouveau_solde": solde_expediteur}

@router.post("/utilisateur/solde")
def consulter_solde(data: shemas.ConsulterSolde, current_utilisateur=Depends(get_current_utilisateur), db: Session = Depends(get_db)):
    verifier_pin_utilisateur(current_utilisateur, data.code_pin, db)

    logger.info(f"Consultation solde : {current_utilisateur.telephone}")

    return {"solde": current_utilisateur.solde}