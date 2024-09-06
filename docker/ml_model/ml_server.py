# Chemin: docker/ml_model/ml_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from predict_model import predict_model
from train_model import train_and_save_model
import joblib
import os

app = FastAPI()

# Vérifier et entraîner le modèle si nécessaire lors du démarrage
@app.on_event("startup")
def startup_event():
    train_and_save_model()

# Modèle pour les données d'entrée
class Features(BaseModel):
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

@app.post("/predict")
async def predict(features: Features):
    """
    Point d'entrée pour les prédictions.
    """
    input_features = features.dict()
    prediction = predict_model(input_features)
    # Assurez-vous que la prédiction soit convertie en type natif Python
    prediction_value = float(prediction[0])
    return {"prediction": prediction_value}

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
