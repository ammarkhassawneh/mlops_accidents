from fastapi import Request
from datetime import datetime
from fastapi.responses import StreamingResponse
import sqlite_utils

db = sqlite_utils.Database("/app/db/data.db")

async def log_request_middleware(request: Request, call_next):
    """
    Middleware pour journaliser chaque requête et sa réponse.
    Enregistre l'adresse IP, l'endpoint, les données d'entrée et de sortie, ainsi que le temps de traitement.
    """
    # Enregistrer le temps de début de la requête
    start_time = datetime.now()
    
    # Exécuter la requête suivante dans la chaîne de middleware
    response = await call_next(request)
    
    # Enregistrer le temps de fin de la requête
    end_time = datetime.now()

    # Vérifier si la réponse est de type StreamingResponse
    if isinstance(response, StreamingResponse):
        # StreamingResponse n'a pas de body directement accessible
        output_data = "StreamingResponse (pas de body disponible)"
    else:
        # Accéder au body de la réponse si disponible
        output_data = response.body.decode() if hasattr(response, 'body') and response.body else "Pas de body"

    # Extraire et enregistrer les informations de la requête et de la réponse
    data = {
        "ip_address": request.client.host,  # Adresse IP du client
        "endpoint": request.url.path,  # L'endpoint de la requête
        "input_data": await request.body(),  # Données d'entrée envoyées par le client
        "output_data": output_data,  # Données de sortie de la réponse
        "timestamp": start_time.isoformat(),  # Timestamp du début de la requête
        "processing_time": (end_time - start_time).total_seconds()  # Temps de traitement en secondes
    }

    # Insérer les logs dans la base de données
    db["request_logs"].insert(data)

    # Retourner la réponse au client
    return response
