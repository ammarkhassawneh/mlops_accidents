from fastapi import Request
from datetime import datetime
import sqlite_utils

db = sqlite_utils.Database("sqlite:////db/data.db")

async def log_request_middleware(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()

    data = {
        "ip_address": request.client.host,
        "endpoint": request.url.path,
        "input_data": request.body(),
        "output_data": response.body(),
        "timestamp": start_time.isoformat(),
        "processing_time": (end_time - start_time).total_seconds()
    }

    db["request_logs"].insert(data)

    return response