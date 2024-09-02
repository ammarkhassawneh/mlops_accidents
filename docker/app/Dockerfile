<<<<<<< HEAD
FROM ubuntu:18.04
#FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    && apt-get clean

RUN git --version

RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt .

# Créez le répertoire pour la base de données
RUN mkdir -p /db && chmod 777 /db

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip install streamlit

COPY . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
=======
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CrÃ©ez le rÃ©pertoire pour la base de donnÃ©es
RUN mkdir -p /db && chmod 777 /db

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
>>>>>>> 36f112f8ecbe942040783f6218ba10150a26e995
