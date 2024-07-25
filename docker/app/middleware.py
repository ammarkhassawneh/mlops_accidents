from fastapi import Request
from datetime import datetime
import sqlite_utils
import os

# Créer le répertoire /db si nécessaire
os.makedirs("/db", exist_ok=True)

'''db = sqlite_utils.Database("sqlite:////db/data.db")'''
db = sqlite_utils.Database("/db/data.db")

async def log_request_middleware(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()

    # Lire les données de la requête et de la réponse
    input_data = await request.body()
    output_data = await response.body()

    data = {
        "ip_address": request.client.host,
        "endpoint": request.url.path,
        "input_data": input_data.decode('utf-8'),
        "output_data": output_data.decode('utf-8'),
        "timestamp": start_time.isoformat(),
        "processing_time": (end_time - start_time).total_seconds()
    }

    # Insérer les données dans la base de données
    db["request_logs"].insert(data)

    return response
