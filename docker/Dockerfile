# Utiliser une image de base officielle Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer git
RUN apt-get update && apt-get install -y git && apt-get clean

# Copier les fichiers de votre projet dans le conteneur
COPY . .

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port que l'application utilisera
EXPOSE 8000

# Commande pour lancer l'application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]