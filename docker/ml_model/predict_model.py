# Chemin: docker/ml_model/predict_model.py

import joblib
import os
from train_model import train_and_save_model
from sklearn.metrics import f1_score
import mlflow
from prometheus_client import Counter, Histogram
from datetime import datetime

# Initialisation des métriques Prometheus
PREDICTION_COUNT = Counter('ml_model_prediction_count', 'Nombre total de prédictions faites')
PREDICTION_LATENCY = Histogram('ml_model_prediction_latency_seconds', 'Temps de latence des prédictions en secondes')

def load_or_train_model():
    model_path = 'trained_model.joblib'
    if os.path.exists(model_path):
        # Charger le modèle entraîné
        model = joblib.load(model_path)
        print("Modèle chargé avec succès.")
        return model
    else:
        # Si le modèle n'existe pas, entraîner un nouveau modèle
        raise FileNotFoundError("Modèle non trouvé, veuillez entraîner le modèle.")

def predict_model(features, true_labels=None):
    with mlflow.start_run():
        model = load_or_train_model()
        features_values = [float(value) for value in features.values()]
        
        # Enregistrer l'heure de début pour mesurer la latence
        start_time = datetime.now()

        # Faire la prédiction
        prediction = model.predict([features_values])

        # Enregistrer la latence
        latency = (datetime.now() - start_time).total_seconds()
        PREDICTION_LATENCY.observe(latency)

        # Incrémenter le compteur de prédictions
        PREDICTION_COUNT.inc()

        # Enregistrer les informations dans MLflow
        mlflow.log_param("input_features", features_values)
        mlflow.log_metric("predicted_value", prediction[0])

        # Si les étiquettes réelles sont fournies, calculer le F1 score
        if true_labels is not None:
            f1 = f1_score([true_labels], [prediction[0]], average='macro')
            mlflow.log_metric("f1_score", f1)

        return prediction
