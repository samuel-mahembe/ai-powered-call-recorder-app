# AI-Powered Call Recorder App

This is a repository for an AI-powered call recorder and analyzer with frontend and backend.

## Docker Setup

This project uses a unified Docker setup that runs both the Angular frontend and FastAPI backend in a single container.

### Architecture

- **Frontend**: Angular 19 application served by nginx on port 80
- **Backend**: FastAPI Python application on port 8000
- **Database**: MongoDB on port 27017
- **Proxy**: nginx routes frontend requests and proxies API calls to the backend

### Quick Start

1. **Clone and navigate to the project**:
   ```bash
   cd ai-powered-call-recorder-app
   ```

2. **Set up environment variables** (optional):
   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. **Run the application**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Services

- **Frontend (port 80)**: Angular application with Material Design
- **Backend API (port 8000)**: FastAPI with real-time transcription and summarization
- **MongoDB (port 27017)**: Data storage for call records and summaries

### Development

To run in development mode:

```bash
# Frontend development
cd frontend
npm install
ng serve

# Backend development  
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Configuration

The nginx configuration automatically:
- Serves static Angular files from `/var/www/html/browser`
- Proxies `/api/*` requests to the FastAPI backend
- Handles WebSocket connections for Socket.IO at `/socket.io/*`

### Environment Variables

- `OPENAI_API_KEY`: Required for AI features (transcription, summarization)
- `MONGODB_URL`: MongoDB connection string (default: mongodb://mongodb:27017)
- `DATABASE_NAME`: Database name (default: ai_call_summarization)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost,http://localhost:80)

### Troubleshooting

1. **Frontend not loading**: Check that nginx is running and the symlink in `/etc/nginx/sites-enabled/` exists
2. **Backend API not accessible**: Verify the FastAPI service is running on port 8000
3. **Database connection issues**: Ensure MongoDB container is running and accessible

### Build Process

The Docker build uses a multi-stage approach:
1. **Frontend Builder**: Builds Angular application using Node.js
2. **Backend Builder**: Installs Python dependencies
3. **Final Stage**: Combines frontend build, backend code, nginx, and runtime dependencies 
