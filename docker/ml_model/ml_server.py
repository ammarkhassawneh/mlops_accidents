# Chemin: docker/ml_model/ml_server.py

from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from predict_model import predict_model
from train_model import train_and_save_model
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import joblib
import os
from starlette.responses import PlainTextResponse
from fastapi import Request

app = FastAPI()

# Définir les métriques Prometheus
REQUEST_COUNT = Counter('ml_model_request_count', 'Nombre total de requêtes reçues pour le modèle')
REQUEST_LATENCY = Histogram('ml_model_request_latency_seconds', 'Temps de latence des requêtes en secondes')
REQUEST_SUCCESS_COUNT = Counter('ml_model_request_success_count', 'Nombre total de requêtes réussies pour le modèle')
REQUEST_ERROR_COUNT = Counter('ml_model_request_error_count', 'Nombre total de requêtes échouées pour le modèle')

# Vérifier et entraîner le modèle si nécessaire lors du démarrage
@app.on_event("startup")
def startup_event():
    train_and_save_model()
    start_http_server(8003)  # Démarrer le serveur Prometheus sur le port 8003

# Middleware pour mesurer les métriques Prometheus
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()  # Incrémente le nombre total de requêtes
    start_time = datetime.now()

    # Exécuter la requête et capturer la réponse
    response = await call_next(request)

    # Calculer la latence
    end_time = datetime.now()
    latency = (end_time - start_time).total_seconds()
    REQUEST_LATENCY.observe(latency)  # Enregistrer la latence
    
    # Enregistrer si la requête a réussi ou échoué
    if response.status_code == 200:
        REQUEST_SUCCESS_COUNT.inc()  # Incrémenter le compteur des requêtes réussies
    else:
        REQUEST_ERROR_COUNT.inc()  # Incrémenter le compteur des requêtes échouées

    return response

# Ajouter une route pour /metrics
@app.get("/metrics")
async def metrics():
    """
    Endpoint pour exposer les métriques Prometheus.
    """
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
    start_time = datetime.now()
    prediction = predict_model(input_features)
    
    # Vérifier si la prédiction est réussie
    if prediction:
        REQUEST_SUCCESS_COUNT.inc()
    else:
        REQUEST_ERROR_COUNT.inc()
    
    # Assurez-vous que la prédiction soit convertie en type natif Python
    prediction_value = float(prediction[0])
    end_time = datetime.now()
    latency = (end_time - start_time).total_seconds()
    REQUEST_LATENCY.observe(latency)
    return {"prediction": prediction_value}

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port=80)
