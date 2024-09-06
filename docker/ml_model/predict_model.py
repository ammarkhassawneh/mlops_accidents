import joblib
import numpy as np
import sklearn
import sys

print(f"NumPy version: {np.__version__}")
print(f"Scikit-learn version: {sklearn.__version__}")

# Charger le modèle
try:
   # loaded_model = joblib.load("trained_model.joblib")
    loaded_model = joblib.load("/ml_model/trained_model.joblib")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    print(f"Python version: {sys.version}")
    print(f"Numpy version: {np.__version__}")
    print(f"Scikit-learn version: {sklearn.__version__}")
    print(f"Joblib version: {joblib.__version__}")
    raise


def predict_severity(model, features):
    prediction = model.predict([features])
    return prediction[0]

# Le reste du code reste inchangé


def predict_model(features):
    input_df = pd.DataFrame([features])
    print(input_df)
    prediction = loaded_model.predict(input_df)
    return prediction

def get_feature_values_manually(feature_names):
    features = {}
    for feature_name in feature_names:
        feature_value = float(input(f"Enter value for {feature_name}: "))
        features[feature_name] = feature_value
    return features

if __name__ == "__main__":
    if len(sys.argv) == 2:
        json_file = sys.argv[1]
        with open(json_file, 'r') as file:
            features = json.load(file)
    else:
        # Assurez-vous que ce fichier existe dans le conteneur Docker
        X_train = pd.read_csv("/ml_model/data/preprocessed/X_train.csv")
        feature_names = X_train.columns.tolist()
        features = get_feature_values_manually(feature_names)

    result = predict_model(features)
    print(f"prediction : {result[0]}")
