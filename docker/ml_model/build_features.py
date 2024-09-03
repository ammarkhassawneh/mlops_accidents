import pandas as pd

def preprocess_features(data):
    # Ajoutez ici votre logique de prétraitement
    # Par exemple :
    df = pd.DataFrame(data, index=[0])
    # Effectuez ici les transformations nécessaires
    return df.values[0]

# Vous pouvez garder d'autres fonctions existantes dans ce fichier
