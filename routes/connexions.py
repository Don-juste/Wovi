from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request,APIRouter,Depends,HTTPException
from datetime import datetime, timedelta
from auth import verifier_mot_de_passe_hashe, generer_otp
from mails import envoyer_otp
from jose import jwt, JWTError
from dependances import limiter,get_db,get_current_utilisateur
from sqlalchemy.orm import Session
from auth import creer_access_token, creer_refresh_token,verifier_otp
from dotenv import load_dotenv
load_dotenv()
import os 
import models
import shemas
import logging
logger = logging.getLogger(__name__)
OTP_EXPIRATION = int(os.getenv("OTP_EXPIRATION"))
RATE_LIMIT=os.getenv("RATE_LIMIT")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router=APIRouter()


MODELES = {"admin": models.Admin, "utilisateur": models.Utilisateur}

@router.post("/utilisateur/connexion")
@limiter.limit(RATE_LIMIT)
def connexion_utilisateur(request: Request, user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.telephone == user.username).first()

    if utilisateur is None:
        nouveau_log = models.LogConnexion(
            telephone=user.username,
            succes=False,
            adresse_ip=request.client.host
        )
        db.add(nouveau_log)
        db.commit()
        logger.warning(f"Tentative de connexion avec un numéro inexistant : {user.username}")
        raise HTTPException(status_code=401, detail="Téléphone ou mot de passe incorrect")

    if not verifier_mot_de_passe_hashe(user.password, utilisateur.mot_de_passe):
        nouveau_log = models.LogConnexion(
            telephone=utilisateur.telephone,
            succes=False,
            adresse_ip=request.client.host
        )
        db.add(nouveau_log)
        db.commit()
        logger.warning(f"Tentative de connexion avec mauvais mot de passe : {utilisateur.telephone}")
        raise HTTPException(status_code=401, detail="Téléphone ou mot de passe incorrect")

    '''code = generer_otp()
    expiration = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION)
    utilisateur.otp_code = code
    utilisateur.otp_expiration = expiration

    nouveau_log = models.LogConnexion(
        telephone=utilisateur.telephone,
        succes=True,
        adresse_ip=request.client.host
    )
    db.add(nouveau_log)
    db.commit()

    await envoyer_otp(utilisateur.email, code)

    logger.info(f"OTP envoyé pour connexion : {utilisateur.telephone}")'''
    access_token = creer_access_token({"sub": utilisateur.telephone, "role": "utilisateur"})
    refresh_token = creer_refresh_token({"sub": utilisateur.telephone, "role": "utilisateur"})

    logger.info(f"Connexion utilisateur finalisée : {utilisateur.telephone}")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


   

@router.post("/admin/connexion")
@limiter.limit(RATE_LIMIT)
def connexion_admin(request: Request, admin: shemas.ConnexionAdmin, db: Session = Depends(get_db)):
    admin_db = db.query(models.Admin).filter(models.Admin.email == admin.email).first()

    if admin_db is None:
        logger.warning(f"Tentative de connexion admin avec un email inexistant : {admin.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if not verifier_mot_de_passe_hashe(admin.mot_de_passe, admin_db.mot_de_passe):
        logger.warning(f"Tentative de connexion admin avec mauvais mot de passe : {admin.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = creer_access_token({"sub": admin_db.email, "role": "admin"})
    refresh_token = creer_refresh_token({"sub": admin_db.email, "role": "admin"})

    logger.info(f"Connexion admin réussie : {admin_db.email}")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/utilisateur/verifier-otp")
def verifier_otp_utilisateur(data: shemas.VerifierOTP, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.telephone == data.telephone).first()
    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Téléphone invalide")

    verifier_otp(utilisateur, data.code)

    utilisateur.otp_code = None
    utilisateur.otp_expiration = None
    db.commit()

    access_token = creer_access_token({"sub": utilisateur.telephone, "role": "utilisateur"})
    refresh_token = creer_refresh_token({"sub": utilisateur.telephone, "role": "utilisateur"})

    logger.info(f"Connexion utilisateur finalisée : {utilisateur.telephone}")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
def rafraichir_token(data: shemas.RefreshToken, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token invalide")

        identifiant = payload.get("sub")
        role = payload.get("role")

        modele = MODELES.get(role)
        if modele is None:
            raise HTTPException(status_code=401, detail="Token invalide")

        champ_identifiant = "email" if role == "admin" else "telephone"
        compte = db.query(modele).filter(getattr(modele, champ_identifiant) == identifiant).first()

        if compte is None:
            raise HTTPException(status_code=401, detail="Token invalide")

        nouveau_access_token = creer_access_token({"sub": identifiant, "role": role})

        return {"access_token": nouveau_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
@router.get("/utilisateur/profil")
def mon_profil(current_utilisateur=Depends(get_current_utilisateur)):
    return {
        "nom": current_utilisateur.nom,
        "prenom": current_utilisateur.prenom,
        "telephone": current_utilisateur.telephone,
        "email": current_utilisateur.email
    }    