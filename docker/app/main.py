from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite_utils
import os
import jwt

# Création de l'application FastAPI avec la documentation incluse
app = FastAPI(
    title="API de Gestion des Utilisateurs et Prédictions",
    description="Cette API permet de gérer les utilisateurs, les prédictions, les journaux de requêtes et les résultats des tests avec des fonctionnalités d'authentification par JWT.",
    version="1.0.0",
    contact={
        "name": ["Ammar", "Patrick", "Yahya"],
        "email": "votre.email@domain.com",
    },
)

# Configuration JWT
SECRET_KEY = "a4e23a65f73b9bc44507ac7be592192d2dd60f273524c0f6d0ebdd30f8d6a660"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Context pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma OAuth2 pour gérer les tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Vérification et création du fichier de base de données si nécessaire
db_path = "/db/data.db"
if not os.path.exists(db_path):
    os.makedirs("/db", exist_ok=True)
    open(db_path, 'a').close()

# Connexion à la base de données SQLite
db = sqlite_utils.Database(db_path)

# Fonction pour s'assurer que les tables sont créées si elles n'existent pas
def create_tables():
    # Création de la table des utilisateurs
    if not db["users"].exists():
        db["users"].create({
            "id": int,
            "name": str,
            "read_rights": str,
            "write_rights": str,
            "hashed_password": str,
            "role": str
        }, pk="id")
    
    # Création de la table des prédictions
    if not db["predictions"].exists():
        db["predictions"].create({
            "id": int,
            "user_id": int,
            "severity": float,
            "latitude": float,
            "longitude": float,
            "timestamp": str
        }, pk="id", foreign_keys=[("user_id", "users", "id")])
    
    # Création de la table des journaux de requêtes
    if not db["request_logs"].exists():
        db["request_logs"].create({
            "id": int,
            "ip_address": str,
            "endpoint": str,
            "input_data": str,
            "output_data": str,
            "timestamp": str
        }, pk="id")
    
    # Création de la table des résultats de tests
    if not db["test_results"].exists():
        db["test_results"].create({
            "id": int,
            "test_name": str,
            "result": bool,
            "timestamp": str
        }, pk="id")

# Appel de la fonction pour créer les tables au démarrage de l'application
create_tables()

# Modèles Pydantic pour gérer les données d'entrée et de sortie
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    read_rights: str
    write_rights: str
    role: str

class UserCreate(BaseModel):
    name: str
    password: str
    read_rights: str
    write_rights: str

class Prediction(BaseModel):
    user_id: int
    severity: float
    latitude: float
    longitude: float

class RequestLog(BaseModel):
    ip_address: str
    endpoint: str
    input_data: str
    output_data: str
    timestamp: str

class TestResult(BaseModel):
    test_name: str
    result: bool
    timestamp: str

# Fonctions auxiliaires pour la gestion des utilisateurs et des tokens
def verify_password(plain_password, hashed_password):
    """Vérifie si le mot de passe est correct en comparant avec le hachage"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hache un mot de passe en utilisant bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crée un token d'accès JWT avec une date d'expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_id(user_id: int):
    """Récupère un utilisateur par son ID dans la base de données"""
    return db["users"].get(user_id)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Récupère l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = db["users"].get(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    """Vérifie si l'utilisateur actuel est un administrateur"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return current_user

# Endpoints pour la gestion des administrateurs
@app.post("/api/admin/login", response_model=Token, tags=["Admin"])
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authentification de l'administrateur. Retourne un token JWT si les informations sont correctes.
    """
    user = db["users"].get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]) or user["role"] != "admin":
        raise HTTPException(status_code=400, detail="Identifiants incorrects ou non administrateur")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["id"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/users", response_model=List[User], tags=["Admin"])
async def manage_users(current_admin: User = Depends(get_current_admin)):
    """
    Récupère la liste de tous les utilisateurs. Accessible uniquement par les administrateurs.
    """
    users = db["users"].rows
    return list(users)

# Endpoints pour la gestion des utilisateurs
@app.post("/api/user/register", response_model=User, tags=["User"])
async def register_user(user: UserCreate):
    """
    Inscription d'un nouvel utilisateur. Retourne les informations de l'utilisateur créé.
    """
    # Vérifier si l'utilisateur existe déjà
    if db["users"].get(user.name):
        raise HTTPException(status_code=400, detail="Le nom d'utilisateur est déjà enregistré")

    # Hacher le mot de passe et insérer l'utilisateur dans la base de données
    hashed_password = get_password_hash(user.password)
    user_id = db["users"].insert({
        "name": user.name,
        "read_rights": user.read_rights,
        "write_rights": user.write_rights,
        "hashed_password": hashed_password,
        "role": "user"
    })
    
    # Récupérer et retourner l'utilisateur créé
    return get_user_by_id(user_id)

@app.get("/api/user/{user_id}", response_model=User, tags=["User"])
async def get_user(user_id: int):
    """
    Récupère les informations d'un utilisateur par son ID.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# Endpoints pour les prédictions
@app.post("/api/predictions", tags=["Predictions"])
async def create_prediction(prediction: Prediction):
    """
    Crée une nouvelle prédiction pour un utilisateur donné.
    """
    db["predictions"].insert({
        "user_id": prediction.user_id,
        "severity": prediction.severity,
        "latitude": prediction.latitude,
        "longitude": prediction.longitude,
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"message": "Prédiction créée avec succès"}

@app.get("/api/predictions/{user_id}", tags=["Predictions"])
async def get_predictions_for_user(user_id: int):
    """
    Récupère toutes les prédictions pour un utilisateur donné.
    """
    predictions = db.query("SELECT * FROM predictions WHERE user_id = ?", [user_id]).fetchall()
    return predictions

# Endpoints pour les journaux de requêtes
@app.get("/api/request_logs", response_model=List[RequestLog], tags=["Logs"])
async def get_request_logs():
    """
    Récupère les journaux de toutes les requêtes effectuées.
    """
    logs = db["request_logs"].rows
    return list(logs)

# Endpoints pour les résultats de tests
@app.post("/api/test_results", tags=["Tests"])
async def log_test_result(result: TestResult):
    """
    Enregistre le résultat d'un test dans la base de données.
    """
    db["test_results"].insert({
        "test_name": result.test_name,
        "result": result.result,
        "timestamp": result.timestamp
    })
    return {"message": "Résultat de test enregistré avec succès"}

@app.get("/api/test_results", response_model=List[TestResult], tags=["Tests"])
async def get_test_results():
    """
    Récupère tous les résultats de tests.
    """
    results = db["test_results"].rows
    return list(results)
