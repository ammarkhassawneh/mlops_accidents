import sqlite3

import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import sqlite_utils
import os
import jwt
import httpx
from geopy.geocoders import Nominatim
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, start_http_server
from prometheus_client import Summary, Gauge
from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from prometheus_client import generate_latest



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

# Définition des compteurs et métriques pour Prometheus
REQUEST_COUNT = Counter('api_request_count', 'Nombre total de requêtes reçues')
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'Temps de latence des requêtes en secondes')
REQUEST_SUCCESS_COUNT = Counter('api_success_request_count', 'Nombre de requêtes réussies')
REQUEST_ERROR_COUNT = Counter('api_error_request_count', 'Nombre de requêtes échouées')

@app.on_event("startup")
async def startup_event():
    start_http_server(8002)




limiter = Limiter(key_func=get_remote_address)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests, please try again later."}
    )

#==================#


app.openapi_tags = [
    {
        "name": "Authentication",  
        "description": "Endpoints pour l'authentification et l'inscription.",
    },
    {
        "name": "Admin",
        "description": "Endpoints pour la gestion des utilisateurs et des administrateurs.",
    },
    {
        "name": "User",
        "description": "Endpoints pour la gestion des utilisateurs.",
    },
    {
        "name": "Predictions",
        "description": "Endpoints pour la gestion des prédictions.",
    },
    {
        "name": "Logs",
        "description": "Endpoints pour consulter les logs.",
    }
]

#================#

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
                "place": int,
                "catu": int,
                "sexe": int,
                "secu1": float,
                "year_acc": int,
                "victim_age": int,
                "catv": int,
                "obsm": int,
                "motor": int,
                "catr": int,
                "circ": int,
                "surf": int,
                "situ": int,
                "vma": float,
                "jour": int,
                "mois": int,
                "lum": int,
                "dep": int,
                "com": int,
                "agg_": int,
                "intt": int,
                "atm": int,
                "col": int,
                "lat": float,
                "long": float,
                "hour": int,
                "nb_victim": int,
                "nb_vehicules": int,
                "predicted_severity": float,
                "timestamp": str
            }, pk="id")
            # Ajout des contraintes sur la latitude, la longitude et la sévérité
            db["predictions"].add_column("predicted_severity", float, not_null=True, check="predicted_severity >= 0 AND predicted_severity <= 1")
            db["predictions"].add_column("lat", float, not_null=True, check="lat >= -90 AND lat <= 90")
            db["predictions"].add_column("long", float, not_null=True, check="long >= -180 AND long <= 180")

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
async def combined_middleware(request: Request, call_next):
    """
    Middleware combiné pour mesurer les métriques Prometheus et enregistrer les logs des requêtes dans la base de données.
    """
    REQUEST_COUNT.inc()  # Incrémente le compteur de requêtes reçues
    start_time = datetime.now(timezone.utc)

    # Lire le corps de la requête une seule fois pour les logs
    body = await request.body()

    try:
        # Appeler le prochain middleware ou route avec la requête modifiée
        response = await call_next(request)

        # Calculer la latence
        end_time = datetime.now(timezone.utc)
        latency = (end_time - start_time).total_seconds()
        REQUEST_LATENCY.observe(latency)  # Enregistrer la latence

        # Enregistrer le succès ou l'échec de la requête
        if response.status_code == 200:
            REQUEST_SUCCESS_COUNT.inc()
        else:
            REQUEST_ERROR_COUNT.inc()

        # Insertion des logs dans la base de données
        db_path = "/app/db/data.db"
        db = sqlite_utils.Database(db_path)
        db["request_logs"].insert({
            "ip_address": request.client.host,
            "endpoint": request.url.path,
            "input_data": body.decode("utf-8") if body else "",
            "output_data": "",  # Vous pouvez adapter ceci si vous avez besoin du corps de la réponse
            "timestamp": start_time.isoformat(),
            "processing_time": latency
        })

    except sqlite3.InterfaceError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion dans la base de données : {e}")

    finally:
        db.conn.close()

    return response

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Endpoint pour exposer les métriques Prometheus.
    """
    return PlainTextResponse(generate_latest(), media_type="text/plain")

# Modèle de requête pour l'API
class PredictionRequest(BaseModel):
    place: int
    catu: int
    sexe: int
    secu1: float
    year_acc: int
    victim_age: int
    catv: int
    obsm: int
    motor: int
    catr: int
    circ: int
    surf: int
    situ: int
    vma: int
    jour: int
    mois: int
    lum: int
    dep: int
    com: int
    agg_: int
    intt: int
    atm: int
    col: int
    lat: float
    long: float
    hour: int
    nb_victim: int
    nb_vehicules: int

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
    """Récupère l'utilisateur actuel et son rôle à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Décoder le token JWT pour obtenir les informations de l'utilisateur
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    
    try:
        # Utiliser rows_where pour récupérer l'utilisateur basé sur son nom d'utilisateur
        user = list(db["users"].rows_where("name = ?", [username]))
        if not user:
            raise credentials_exception
        user = user[0]  # Obtenir la première entrée (l'utilisateur trouvé)
        
        # Vérifier si le rôle dans le token correspond au rôle de la base de données
        if user["role"] != role:
            raise credentials_exception
        
        return user
    finally:
        db.conn.close()




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



# Endpoints pour la gestion des utilisateurs et des administrateurs
@app.post("/api/user/register", response_model=User, tags=["Authentication"])
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

# Fonction pour l'authentification de l'utilisateur avec Prometheus intégré
@app.post("/api/auth/token", response_model=Token, tags=["Authentication"])
@limiter.limit("3/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authentification des utilisateurs avec mesure des métriques Prometheus.
    """
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        user = authenticate_user(form_data.username, form_data.password)

        if not user:
            REQUEST_ERROR_COUNT.inc()  # Incrémenter les erreurs
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nom d'utilisateur ou mot de passe incorrect")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user["name"], "role": user["role"]}, expires_delta=access_token_expires)

        log_activity(user["id"], f"Connexion réussie en tant que {user['role']}")
        REQUEST_SUCCESS_COUNT.inc()  # Incrémenter les succès

        return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

#=====================#
@app.get("/admin/dashboard", tags=["Admin"])
async def admin_dashboard(current_admin: User = Depends(get_current_user)):
    """
    Interface simple pour les administrateurs afin de visualiser le tableau de bord.
    Cette route permet de visualiser les utilisateurs et prédictions actuelles.
    """
    if current_admin["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions insuffisantes")
    
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    
    try:
        # Récupérer les utilisateurs
        users = list(db["users"].rows)
        # Récupérer les prédictions
        predictions = list(db["predictions"].rows)
    
        # Retourner un aperçu général des utilisateurs et des prédictions
        return {
            "users_count": len(users),
            "predictions_count": len(predictions),
            "latest_users": users[:5],  # Afficher les 5 derniers utilisateurs
            "latest_predictions": predictions[:5]  # Afficher les 5 dernières prédictions
        }
    finally:
        db.conn.close()

@app.delete("/admin/users/{user_id}", tags=["Admin"])
async def delete_user(user_id: int, current_admin: User = Depends(get_current_user)):
    """
    Supprimer un utilisateur par ID (uniquement pour les administrateurs).
    """
    
    if current_admin["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions insuffisantes")
    
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        db["users"].delete(user_id)
        return {"message": f"Utilisateur {user_id} supprimé avec succès."}
    finally:
        db.conn.close()

@app.put("/admin/users/{user_id}", tags=["Admin"])
async def update_user_rights(user_id: int, read_rights: str, write_rights: str, current_admin: User = Depends(get_current_user)):
    """
    Mise à jour des droits de lecture et d'écriture pour un utilisateur.
    """
    
    if current_admin["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions insuffisantes")
    
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        db["users"].update(user_id, {"read_rights": read_rights, "write_rights": write_rights})
        return {"message": f"Droits de l'utilisateur {user_id} mis à jour avec succès."}
    finally:
        db.conn.close()


@app.put("/users/me", response_model=User, tags=["User"])
async def update_user_info(name: Optional[str] = None, email: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """
    Mettre à jour les informations personnelles de l'utilisateur connecté.
    """
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        if update_data:
            db["users"].update(current_user["id"], update_data)
        return get_user_by_id(current_user["id"])
    finally:
        db.conn.close()

#=========================#

@app.get("/api/admin/users", response_model=List[User], tags=["Admin"])
async def manage_users(current_admin: User = Depends(get_current_user)):
    
    if current_admin["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissions insuffisantes")
    
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        users = db["users"].rows
        return list(users)
    finally:
        db.conn.close()

@app.post("/api/predictions", tags=["Predictions"])
async def create_prediction(prediction: PredictionRequest, current_user: dict = Depends(get_current_user)):
    """
    Crée une nouvelle prédiction en envoyant les données au modèle ML et en sauvegardant le résultat dans la base de données.
    Cette fonction récupère également l'ID de l'utilisateur actuellement authentifié.
    """
    ml_model_url = "http://ml_model:80/predict"  
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    
    try:
        # Envoyer la requête au modèle ML pour obtenir la prédiction
        async with httpx.AsyncClient() as client:
            response = await client.post(ml_model_url, json=prediction.dict(), timeout=30.0)
        
        # Vérifier si la requête au modèle a réussi
        if response.status_code == 200:
            result = response.json()
            severity = result["prediction"]  
            
            # Obtenir le user_id de l'utilisateur authentifié
            user_id = current_user["id"]
            
            # Insérer la prédiction dans la base de données
            db["predictions"].insert({
                "user_id": user_id,  # Utiliser l'user_id de l'utilisateur actuel
                "place": prediction.place,
                "catu": prediction.catu,
                "sexe": prediction.sexe,
                "secu1": prediction.secu1,
                "year_acc": prediction.year_acc,
                "victim_age": prediction.victim_age,
                "catv": prediction.catv,
                "obsm": prediction.obsm,
                "motor": prediction.motor,
                "catr": prediction.catr,
                "circ": prediction.circ,
                "surf": prediction.surf,
                "situ": prediction.situ,
                "vma": prediction.vma,
                "jour": prediction.jour,
                "mois": prediction.mois,
                "lum": prediction.lum,
                "dep": prediction.dep,
                "com": prediction.com,
                "agg_": prediction.agg_,
                "intt": prediction.intt,
                "atm": prediction.atm,
                "col": prediction.col,
                "lat": prediction.lat,
                "long": prediction.long,
                "hour": prediction.hour,
                "nb_victim": prediction.nb_victim,
                "nb_vehicules": prediction.nb_vehicules,
                "predicted_severity": severity,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Enregistrer l'activité de l'utilisateur
            log_activity(user_id, "Création d'une nouvelle prédiction")
            
            # Retourner le message et la prédiction à l'utilisateur
            return {"message": "Prédiction créée avec succès", "severity": severity}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de la prédiction")
    
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Timeout lors de la connexion au service de prédiction")
    
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Erreur de requête: {exc}")
    
    finally:
        db.conn.close()


#===========================#

@app.get("/api/predictions/{user_id}", tags=["Predictions"])
async def get_predictions_for_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Récupère les prédictions pour un utilisateur donné.
    - Les administrateurs peuvent voir les prédictions de tout utilisateur.
    - Les utilisateurs normaux peuvent voir uniquement leurs propres prédictions.
    """
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    
    try:
        # Si l'utilisateur est admin, il peut voir toutes les prédictions
        if current_user["role"] == "admin":
            predictions = list(db.query("SELECT * FROM predictions WHERE user_id = ?", [user_id]))
        # Si l'utilisateur est un utilisateur normal, il ne peut voir que ses propres prédictions
        elif current_user["id"] == user_id:
            predictions = list(db.query("SELECT * FROM predictions WHERE user_id = ?", [user_id]))
        else:
            raise HTTPException(status_code=403, detail="Accès refusé : vous ne pouvez voir que vos propres prédictions.")
        
        return predictions
    finally:
        db.conn.close()
        
#=========================#


# Endpoints pour les journaux de requêtes
@app.get("/api/request_logs", response_model=List[RequestLog], tags=["Logs"])
async def get_request_logs(current_admin: dict = Depends(get_current_user)):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        logs = db["request_logs"].rows
        return list(logs)
    finally:
        db.conn.close()

# Endpoints pour les résultats de tests
@app.post("/api/test_results", tags=["Tests"])
async def log_test_result(result: TestResult, current_admin: dict = Depends(get_current_user)):
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
async def get_test_results(current_admin: dict = Depends(get_current_user)):
    db_path = "/app/db/data.db"
    db = sqlite_utils.Database(db_path)
    try:
        results = db["test_results"].rows
        return list(results)
    finally:
        db.conn.close()

