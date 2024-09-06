import joblib
import os
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

def train_and_save_model():
    # Chargement des données d'entraînement
    X_train = pd.read_csv('data/preprocessed/X_train.csv')
    y_train = pd.read_csv('data/preprocessed/y_train.csv')
    y_train = np.ravel(y_train)
    
    # Créer et entraîner le modèle
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Sauvegarder le modèle
    joblib.dump(model, 'trained_model.joblib')
    print("Modèle entraîné et sauvegardé avec succès.")

if __name__ == "__main__":
    train_and_save_model()
