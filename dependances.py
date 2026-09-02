from fastapi import HTTPException,Depends 
from auth import verifier_token
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
from database import SessionLocal
from models import Utilisateur,Admin
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="utilisateur/connexion")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_utilisateur(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verifier_token(token)
    if payload["role"] != "utilisateur":
        raise HTTPException(status_code=403, detail="Accès réservé aux utilisateurs")
    utilisateur = db.query(Utilisateur).filter(Utilisateur.telephone == payload["identifiant"]).first()
    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    return utilisateur


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verifier_token(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux admins")
    admin = db.query(Admin).filter(Admin.email == payload["identifiant"]).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    return admin            