# main.py
from fastapi import FastAPI
from .middleware import log_request_middleware  # Importer le middleware
import sqlite_utils

@app.get("/")
def read_root():
    return {"Hello": "World"}

app = FastAPI()

# Enregistrer le middleware
app.middleware("http")(log_request_middleware)

db = sqlite_utils.Database("/db/data.db")

docker-compose exec app ls -l /db