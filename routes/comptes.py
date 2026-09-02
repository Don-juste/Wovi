from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from dependances import get_db
import models
import shemas
from auth import hashe_mot_de_passe, hashe_pin
from dotenv import load_dotenv
load_dotenv()
import os
import logging

logger = logging.getLogger(__name__)

ADMIN_KEY = os.getenv("ADMIN_KEY")

router = APIRouter()


@router.post("/utilisateur/creer-compte")
def creer_compte_utilisateur(user: shemas.UtilisateurCreate, db: Session = Depends(get_db)):
    telephone_existant = db.query(models.Utilisateur).filter(models.Utilisateur.telephone == user.telephone).first()
    if telephone_existant:
        raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà utilisé")

    email_existant = db.query(models.Utilisateur).filter(models.Utilisateur.email == user.email).first()
    if email_existant:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    nouvel_utilisateur = models.Utilisateur(
        nom=user.nom,
        prenom=user.prenom,
        telephone=user.telephone,
        email=user.email,
        mot_de_passe=hashe_mot_de_passe(user.mot_de_passe),
        code_pin=hashe_pin(user.code_pin)
    )

    db.add(nouvel_utilisateur)
    db.commit()
    db.refresh(nouvel_utilisateur)

    logger.info(f"Nouveau compte utilisateur créé : {user.telephone}")

    return {"Message": "Compte créé avec succès"}


@router.post("/admin/creer-compte")
def creer_compte_admin(admin: shemas.AdminCreate, x_admin_key: str = Header(...), db: Session = Depends(get_db)):
    if ADMIN_KEY != x_admin_key:
        logger.warning("Tentative de création admin refusée avec une mauvaise clé")
        raise HTTPException(status_code=401, detail="Accès refusé")

    email_existant = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    if email_existant:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    nouvel_admin = models.Admin(
        nom=admin.nom,
        prenom=admin.prenom,
        email=admin.email,
        mot_de_passe=hashe_mot_de_passe(admin.mot_de_passe)
    )
    db.add(nouvel_admin)
    db.commit()
    db.refresh(nouvel_admin)

    logger.info(f"Nouveau compte admin créé : {admin.email}")

    return {"Message": "Compte admin créé avec succès"}