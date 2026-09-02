from datetime import datetime,timedelta
import random
from fastapi import HTTPException
from jose import jwt,JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
load_dotenv()
import os
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRATION=int(os.getenv("ACCESS_TOKEN_EXPIRATION"))
REFRESH_TOKEN_EXPIRATION=int(os.getenv("REFRESH_TOKEN_EXPIRATION"))
pwd_context=CryptContext(schemes=["bcrypt"])
def hashe_mot_de_passe(mot_de_passe:str):
    return pwd_context.hash(mot_de_passe)
def verifier_mot_de_passe_hashe(mot_de_passe:str,mot_de_passe_hashe:str):
    return pwd_context.verify(mot_de_passe,mot_de_passe_hashe)

def hashe_pin(pin: str):
    return pwd_context.hash(pin)

def verifier_pin_hashe(pin: str, pin_hashe: str):
    return pwd_context.verify(pin, pin_hashe)

def generer_otp():
    return str(random.randint(100000,999999))

def verifier_otp(user,code:str):
    if user.otp_code!=code:
        raise HTTPException(status_code=401,detail="Code OTP incorrect")
    if datetime.utcnow() > user.otp_expiration :
        raise HTTPException(status_code=401,detail="Code OTP expiré")
    return True
        
        
def creer_access_token(data:dict):
    data_copie=data.copy()
    expiration=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
    data_copie.update({"exp":expiration, "type":"access"})
    token=jwt.encode(data_copie,SECRET_KEY,algorithm=ALGORITHM)
    return token

def creer_refresh_token(data:dict):
    data_copie=data.copy()
    expiration=datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRATION)
    data_copie.update({"exp":expiration, "type":"refresh"})
    token=jwt.encode(data_copie,SECRET_KEY,algorithm=ALGORITHM)
    return token

def verifier_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token invalide")
        identifiant = payload.get("sub")
        role = payload.get("role")
        if identifiant is None or role is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"identifiant": identifiant, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
