FROM ubuntu:18.04

# Mettre à jour les paquets et installer les dépendances
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    && apt-get clean

# Vérifier la version de git
RUN git --version

# Mettre à jour pip
RUN pip3 install --upgrade pip

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Créer le répertoire pour la base de données
RUN mkdir -p /db && chmod 777 /db

# Installer les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application dans le répertoire de travail
COPY . .

# Exposer le port 80
EXPOSE 80

# Définir la commande pour exécuter l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
