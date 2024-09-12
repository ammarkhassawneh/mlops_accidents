# Chemin: docker/ml_model/train_model.py

import joblib
import os
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
import mlflow
import mlflow.sklearn

def train_and_save_model():
    # Définir l'expérience MLflow
    mlflow.set_experiment("my_experiment")

    # Chargement des données d'entraînement
    X_train = pd.read_csv('data/preprocessed/X_train.csv')
    y_train = pd.read_csv('data/preprocessed/y_train.csv')
    y_train = np.ravel(y_train)

    # Créer et entraîner le modèle
    model = RandomForestClassifier()

    with mlflow.start_run():
        # Entraîner le modèle
        model.fit(X_train, y_train)

        # Prédiction sur les données d'entraînement
        y_pred = model.predict(X_train)
        
        # Calculer le F1 score
        f1 = f1_score(y_train, y_pred, average='macro')
        print(f"F1 Score: {f1}")

        # Enregistrer le modèle et les métriques avec MLflow
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_metric("f1_score", f1)
        
        # Sauvegarder le modèle
        joblib.dump(model, 'trained_model.joblib')
        mlflow.sklearn.log_model(model, "model")
        print("Modèle entraîné et sauvegardé avec succès.")
        
        # Vérifier si le F1 score est inférieur à 60%
        if f1 < 0.60:
            print("Le F1 score est inférieur à 60%! Envoi de l'alerte...")

if __name__ == "__main__":
    train_and_save_model()
