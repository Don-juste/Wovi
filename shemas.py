from pydantic import BaseModel,Field,field_validator 
import re 
class UtilisateurCreate(BaseModel):
    nom: str=Field(min_length=2,max_length=53)
    prenom: str=Field(min_length=3,max_length=53)
    telephone: str=Field(min_length=10,max_length=10)
    email: str
    mot_de_passe: str=Field(min_length=8)
    code_pin: str=Field(min_length=4,max_length=4)
    
    @field_validator("nom")
    def valider_nom(cls, nom):
        if not re.search(r"^[A-Z]+$", nom):
           raise ValueError("Le nom doit être entièrement en majuscules")
        return nom

    @field_validator("prenom")
    def valider_prenom(cls, prenom):
        if not re.search(r"^[A-Z][a-z-]+$", prenom):
           raise ValueError("Le prénom doit commencer par une majuscule")
        return prenom

    @field_validator("email")
    def valider_email(cls, email):
        if not re.search(r"^[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]+$", email):
            raise ValueError("Email invalide")
        return email

    @field_validator("telephone")
    def valider_telephone(cls, telephone):
        if not re.search(r"^01\d{8}$", telephone):
           raise ValueError("Le numéro doit commencer par 01 suivi de 8 chiffres")
        return telephone
    
    @field_validator("mot_de_passe")
    def valider_mot_de_passe(cls, mot_de_passe):
        if not re.search(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@#!]).{8,}$", mot_de_passe):
           raise ValueError("Le mot de passe doit contenir une majuscule, un chiffre, un caractère spécial (@#!) et faire au moins 8 caractères")
        return mot_de_passe
    
    @field_validator("code_pin")
    def valider_pin(cls, pin):
        if not pin.isdigit():
            raise ValueError("Le code PIN doit contenir uniquement des chiffres")
        return pin
    
class AdminCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    mot_de_passe: str
    
class VerifierOTP(BaseModel):
    telephone: str
    code: str

class DepotRequest(BaseModel):
    montant: float=Field(gt=0)
    code_pin: str
        
class RetraitRequest(BaseModel):
    montant: float=Field(gt=0)
    code_pin: str
    
class VerifierDestinataire(BaseModel):
    telephone: str

class TransfertRequest(BaseModel):
    telephone_destinataire: str
    montant: float=Field(gt=0)
    code_pin: str

class ConsulterSolde(BaseModel):
    code_pin: str

class DebloquerCompte(BaseModel):
    telephone: str
    
class Token(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str 

class RefreshToken(BaseModel):
    refresh_token:str       

class ConnexionAdmin(BaseModel):
    email: str
    mot_de_passe: str                              
        