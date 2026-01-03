FROM python:3.11-slim

# Set working directory
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

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for audio processing
RUN mkdir -p /tmp/ai_call_audio

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the hackathon-optimized CallGist application
CMD ["uvicorn", "hackathon_main:app", "--host", "0.0.0.0", "--port", "8000"]
