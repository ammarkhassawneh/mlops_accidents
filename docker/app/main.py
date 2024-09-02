import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import sqlite_utils
import os
import jwt
from geopy.geocoders import Nominatim

# from middleware import log_request_middleware  # Importer le middleware
# import httpx

# Création de l'application FastAPI avec la documentation incluse
app = FastAPI(
    title="API de Gestion des Utilisateurs et Prédictions",
    description="Cette API permet de gérer les utilisateurs, les prédictions, les journaux de requêtes et les résultats des tests avec des fonctionnalités d'authentification par JWT.",
    version="1.0.0",
    contact={
        "name": "Patrick, Ammar, Yahya",
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

# Fonction pour s'assurer que les tables sont créées si elles n'existent pas
def create_tables():
    """
    Fonction pour créer toutes les tables dans la base de données si elles n'existent pas déjà.
    """
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        # Création de la table des utilisateurs
        if not db["users"].exists():
            db["users"].create({
                "id": int,
                "name": str,
                "email": str,
                "hashed_password": str,
                "read_rights": str,
                "write_rights": str,
                "role": str,
                "created_at": str
            }, pk="id")
            # Ajout des contraintes supplémentaires et vérifications
            db.execute("ALTER TABLE users ADD CONSTRAINT unique_name UNIQUE (name)")
            db.execute("ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email)")

        # Création de la table des prédictions
        if not db["predictions"].exists():
            db["predictions"].create({
                "id": int,
                "user_id": int,
                "severity": float,
                "latitude": float,
                "longitude": float,
                "timestamp": str
            }, pk="id")
            # Ajout des contraintes sur la latitude, la longitude et la sévérité
            db["predictions"].add_column("severity", float, not_null=True, check="severity >= 0 AND severity <= 1")
            db["predictions"].add_column("latitude", float, not_null=True, check="latitude >= -90 AND latitude <= 90")
            db["predictions"].add_column("longitude", float, not_null=True, check="longitude >= -180 AND longitude <= 180")

        # Création de la table des journaux de requêtes
        if not db["request_logs"].exists():
            db["request_logs"].create({
                "id": int,
                "ip_address": str,
                "endpoint": str,
                "input_data": str,
                "output_data": str,
                "timestamp": str,
                "processing_time": float
            }, pk="id")

        # Création de la table des journaux d'activités
        if not db["activity_logs"].exists():
            db["activity_logs"].create({
                "id": int,
                "user_id": int,
                "activity": str,
                "timestamp": str
            }, pk="id")
            # Ajout de la clé étrangère avec suppression en cascade
            db["activity_logs"].add_foreign_key("user_id", "users", "id", on_delete="CASCADE")

        # Création de la table des résultats de tests
        if not db["test_results"].exists():
            db["test_results"].create({
                "id": int,
                "test_name": str,
                "result": bool,
                "timestamp": str
            }, pk="id")

    finally:
        db.conn.close()

    print("Tables créées ou déjà existantes avec succès.")

# Appel de la fonction pour créer les tables au démarrage de l'application
create_tables()

@app.middleware("http")
# Middleware pour enregistrer les logs des requêtes
async def log_request_middleware(request: Request, call_next):
    """
    Middleware pour enregistrer les logs des requêtes.
    """
    start_time = datetime.now(timezone.utc)

    # Lire le corps de la requête une seule fois
    body = await request.body()

    # Appeler le prochain middleware ou route avec la requête modifiée
    response = await call_next(request)

    # Calculer le temps de fin et la durée de traitement
    end_time = datetime.now(timezone.utc)
    processing_time = (end_time - start_time).total_seconds()

    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        # Insertion des logs dans la base de données
        db["request_logs"].insert({
            "ip_address": request.client.host,
            "endpoint": request.url.path,
            "input_data": body.decode("utf-8") if body else "",
            "output_data": "",  # Vous devez ajuster cette partie si vous avez besoin du corps de la réponse
            "timestamp": start_time.isoformat(),
            "processing_time": processing_time
        })
    except sqlite3.InterfaceError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion dans la base de données : {e}")
    finally:
        db.conn.close()

    return response

# Modèles Pydantic pour gérer les données d'entrée et de sortie
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    email: str
    read_rights: str
    write_rights: str
    role: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    read_rights: str
    write_rights: str

class Prediction(BaseModel):
    user_id: int
    severity: float
    latitude: float
    longitude: float

    @validator('severity')
    def check_severity(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Severity must be between 0 and 1')
        return v

    @validator('latitude')
    def check_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def check_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_id(user_id: int):
    """Récupère un utilisateur par son ID dans la base de données"""
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        return db["users"].get(user_id)
    finally:
        db.conn.close()

# Fonction pour enregistrer une activité dans les logs
def log_activity(user_id: int, activity: str):
    """
    Enregistre une activité pour un utilisateur dans le journal des activités.
    """
    # Vérification que user_id est un entier
    if not isinstance(user_id, int):
        raise ValueError("user_id doit être un entier")

    # Vérification que l'activité est une chaîne de caractères
    if not isinstance(activity, str):
        raise ValueError("L'activité doit être une chaîne de caractères")

    # Utilisation de datetime avec timezone UTC pour timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        # Insertion dans la base de données
        db["activity_logs"].insert({
            "user_id": int(user_id),
            "activity": activity,
            "timestamp": timestamp  # Assurez-vous que c'est une chaîne de caractères ISO 8601
        })
    except sqlite3.InterfaceError as e:
        raise ValueError(f"Erreur lors de l'insertion dans la base de données : {e}")
    finally:
        db.conn.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Récupère l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Décoder le token JWT pour obtenir le nom d'utilisateur
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    # Connexion à la base de données
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        # Rechercher l'utilisateur dans la base de données par nom d'utilisateur
        users = list(db["users"].rows_where("name = ?", [token_data.username]))
        if not users:
            raise credentials_exception
        user = users[0]  # Prendre le premier résultat si l'utilisateur existe
        return user
    finally:
        # Fermer la connexion à la base de données
        db.conn.close()


def get_current_admin(current_user: User = Depends(get_current_user)):
    """Vérifie si l'utilisateur actuel est un administrateur"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return current_user

def authenticate_user(username: str, password: str):
    """
    Authentifie un utilisateur dans la base de données.
    Vérifie si l'utilisateur existe et si le mot de passe est correct.
    """
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        user = list(db["users"].rows_where("name = ?", [username]))
        if len(user) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nom d'utilisateur incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = user[0]
        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.conn.close()

@app.post("/api/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["name"]}, expires_delta=access_token_expires)
    log_activity(user["id"], "Connexion réussie")
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints pour la gestion des utilisateurs et des administrateurs
@app.post("/api/user/register", response_model=User, tags=["User"])
async def register_user(user: UserCreate):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        existing_user = list(db["users"].rows_where("name = ?", [user.name]))
        if existing_user:
            raise HTTPException(status_code=400, detail="Le nom d'utilisateur est déjà enregistré")

        # Vérifier si c'est le premier utilisateur, s'il est admin, sinon user
        role = "admin" if db["users"].count == 0 else "user"

        hashed_password = get_password_hash(user.password)
        user_data = {
            "name": user.name,
            "email": user.email,
            "read_rights": user.read_rights,
            "write_rights": user.write_rights,
            "hashed_password": hashed_password,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        db["users"].insert(user_data)
        user_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        log_activity(int(user_id), "Inscription d'un nouvel utilisateur")
        return get_user_by_id(user_id)
    finally:
        db.conn.close()

@app.post("/api/admin/login", response_model=Token, tags=["Admin"])
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user["role"] != "admin":
        raise HTTPException(status_code=400, detail="L'utilisateur n'est pas un administrateur")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["name"]}, expires_delta=access_token_expires)
    log_activity(user["id"], "Connexion de l'administrateur")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/users", response_model=List[User], tags=["Admin"])
async def manage_users(current_admin: User = Depends(get_current_admin)):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        users = db["users"].rows
        return list(users)
    finally:
        db.conn.close()

# Endpoints pour les prédictions
@app.post("/api/predictions", tags=["Predictions"])
async def create_prediction(prediction: Prediction):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        db["predictions"].insert({
            "user_id": prediction.user_id,
            "severity": prediction.severity,
            "latitude": prediction.latitude,
            "longitude": prediction.longitude,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        log_activity(prediction.user_id, "Création d'une nouvelle prédiction")
        return {"message": "Prédiction créée avec succès"}
    finally:
        db.conn.close()

@app.get("/api/predictions/{user_id}", tags=["Predictions"])
async def get_predictions_for_user(user_id: int):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        predictions = list(db.query("SELECT * FROM predictions WHERE user_id = ?", [user_id]))
        return predictions
    finally:
        db.conn.close()

# Endpoints pour les journaux de requêtes
@app.get("/api/request_logs", response_model=List[RequestLog], tags=["Logs"])
async def get_request_logs():
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        logs = db["request_logs"].rows
        return list(logs)
    finally:
        db.conn.close()

# Endpoints pour les résultats de tests
@app.post("/api/test_results", tags=["Tests"])
async def log_test_result(result: TestResult):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        db["test_results"].insert({
            "test_name": result.test_name,
            "result": result.result,
            "timestamp": result.timestamp
        })
        return {"message": "Résultat de test enregistré avec succès"}
    finally:
        db.conn.close()

@app.get("/api/test_results", response_model=List[TestResult], tags=["Tests"])
async def get_test_results():
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        results = db["test_results"].rows
        return list(results)
    finally:
        db.conn.close()
