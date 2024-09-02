FROM python:3.11.9

WORKDIR /ml_model

RUN pip install --no-cache-dir --upgrade pip

# Installer une version spécifique de numpy
RUN pip install --no-cache-dir numpy==1.23.5

# Installer scikit-learn séparément
RUN pip install --no-cache-dir scikit-learn==1.4.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier d'abord les fichiers Python nécessaires
COPY ml_server.py predict_model.py build_features.py ./

# Copier le modèle entraîné
COPY trained_model.joblib .

# Assurez-vous que le dossier data est copié dans le conteneur si nécessaire
COPY ./data /ml_model/data

# Copier tous les autres fichiers restants
COPY . .

CMD ["python", "ml_server.py"]
