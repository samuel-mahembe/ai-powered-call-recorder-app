# Multi-stage build for frontend and backend

# Stage 1: Build Angular frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies (including dev dependencies for build)
RUN npm ci --legacy-peer-deps

# Copy frontend source code
COPY frontend/ .

# Build Angular application
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies including OPUS support
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libopus0 \
    libopus-dev \
    opus-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libopus0 \
    libopus-dev \
    opus-tools \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from backend-builder stage
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY backend/ .

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist/materialm /var/www/html

# Create directory for audio processing
RUN mkdir -p /tmp/ai_call_audio

# Configure nginx to serve frontend and proxy backend API
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Create startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 80 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost || exit 1

# Start both services
CMD ["/app/start.sh"]
