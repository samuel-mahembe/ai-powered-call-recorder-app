#!/bin/bash
# Start nginx in background
nginx -g 'daemon off;' &

# Start FastAPI backend
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000
