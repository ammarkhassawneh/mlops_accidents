from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from geopy.geocoders import Nominatim
import sqlite_utils
import os
from middleware import log_request_middleware  # Importer le middleware
import httpx

app = FastAPI()
db_path = "/db/data.db"
geolocator = Nominatim(user_agent="my_app")

# Créer le répertoire /db si nécessaire
os.makedirs("/db", exist_ok=True)

# Enregistrer le middleware
app.middleware("http")(log_request_middleware)

# Vérifiez si la base de données existe, sinon créez-la
if not os.path.exists(db_path):
    db = sqlite_utils.Database(db_path)
    with open("/app/schema.sql", "r") as schema_file:
        db.executescript(schema_file.read())
else:
    db = sqlite_utils.Database(db_path)

class User(BaseModel):
    id: int
    name: str
    read_rights: List[str]
    write_rights: List[str]

class PredictionRequest(BaseModel):
    location: str

@app.post("/api/users")
def create_user(user: User):
    # Validate rights and create user
    pass

@app.get("/api/users", response_model=List[User])
def get_users():
    # Fetch users with pagination and filters
    pass

@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int):
    # Fetch user details
    pass

@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: User):
    # Update user information based on rights
    pass

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    # Delete user based on rights
    pass

@app.post("/api/predictions")
def predict_severity(request: PredictionRequest):
    location = geolocator.geocode(request.location)
    if not location:
        raise HTTPException(status_code=400, detail="Invalid location")

    # Perform ML prediction using the location data
    # Store prediction result and request logs in the database
    pass

@app.get("/api/predictions")
def get_predictions():
    # Fetch predictions with pagination and filters
    pass

@app.get("/api/predictions/{prediction_id}")
def get_prediction(prediction_id: int):
    # Fetch prediction details
    pass

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Le reste de votre code FastAPI ici

@app.post("/api/predictions")
async def predict_severity(request: PredictionRequest):
    location = geolocator.geocode(request.location)
    if not location:
        raise HTTPException(status_code=400, detail="Invalid location")

    # Appel au service ML
    async with httpx.AsyncClient() as client:
        response = await client.post("http://ml_model:5000/predict", json={
            "latitude": location.latitude,
            "longitude": location.longitude
        })
    prediction = response.json()

    # Stocker la prédiction dans la base de données
    # (à implémenter)

    return prediction
