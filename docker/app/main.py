from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from geopy.geocoders import Nominatim
import sqlite_utils

app = FastAPI()
db = sqlite_utils.Database("sqlite:////db/data.db")
geolocator = Nominatim(user_agent="my_app")

class User(BaseModel):
    id: int
    name: str
    read_rights: List[str]
    write_rights: List[str]

class PredictionRequest(BaseModel):
    location: str

# main.py
from fastapi import FastAPI
from .test_api import router as test_router  # Importer le routeur de test

app = FastAPI()

# Enregistrer le routeur de test
app.include_router(test_router)


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