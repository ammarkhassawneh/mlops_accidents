FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Créez le répertoire pour la base de données
RUN mkdir -p /db && chmod 777 /db

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]