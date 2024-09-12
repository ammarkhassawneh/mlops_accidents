# Dockerfile pour le service ml_model

# Utiliser une image Python 3.11.9
FROM python:3.11.9

# Définir le répertoire de travail dans la conteneur
WORKDIR /ml_model

# Installer les outils nécessaires pour construire les bibliothèques comme gcc
RUN apt-get update && apt-get install -y build-essential gcc

# Mettre à jour pip pour avoir la dernière version
RUN pip install --no-cache-dir --upgrade pip

# Copier le fichier des dépendances et installer les paquets requis
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts Python nécessaires
COPY ml_server.py predict_model.py train_model.py build_features.py ./

# Copier les données nécessaires si elles existent dans le dossier data local
COPY ./data /ml_model/data

EXPOSE 80

# Vérifier si le modèle est déjà entraîné (fichier trained_model.joblib)
# Si le modèle n'existe pas, entraîner un nouveau modèle avant de lancer le serveur Uvicorn
CMD ["/bin/bash", "-c", "if [ ! -f trained_model.joblib ]; then python train_model.py; fi && uvicorn ml_server:app --host 0.0.0.0 --port 80"]
