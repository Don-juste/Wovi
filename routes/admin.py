from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependances import get_db, get_current_admin
import models
import shemas
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.put("/admin/debloquer-compte")
def debloquer_compte(data: shemas.DebloquerCompte, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.telephone == data.telephone).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    utilisateur.compte_bloque = False
    utilisateur.tentatives_pin_echouees = 0
    db.commit()

    logger.info(f"Compte débloqué par admin {current_admin.email} : utilisateur {utilisateur.telephone}")

    return {"Message": "Compte débloqué avec succès"}


@router.get("/admin/statistiques")
def statistiques(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    nombre_transactions = db.query(models.Transaction).count()
    montant_total = db.query(func.sum(models.Transaction.montant)).scalar() or 0
    nombre_tentatives_echouees = db.query(models.LogConnexion).filter(models.LogConnexion.succes == False).count()
    nombre_utilisateurs = db.query(models.Utilisateur).count()
    nombre_comptes_bloques = db.query(models.Utilisateur).filter(models.Utilisateur.compte_bloque == True).count()

    return {
        "nombre_transactions": nombre_transactions,
        "montant_total_transactions": montant_total,
        "nombre_tentatives_connexion_echouees": nombre_tentatives_echouees,
        "nombre_utilisateurs": nombre_utilisateurs,
        "nombre_comptes_bloques": nombre_comptes_bloques
    }