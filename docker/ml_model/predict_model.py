import joblib
import os
from train_model import train_and_save_model

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

def predict_model(features):
    # Charger ou entraîner le modèle
    model = load_or_train_model()
    
    # Conversion des caractéristiques en liste de valeurs
    features_values = list(features.values())
    
    # Assurez-vous que toutes les valeurs sont des flottants
    features_values = [float(value) for value in features_values]
    
    # Faire la prédiction
    prediction = model.predict([features_values])
    return prediction
