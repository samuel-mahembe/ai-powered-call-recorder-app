# AI Call Summarization Backend

A powerful FastAPI-based backend system for real-time call transcription, AI-driven summarization, sentiment analysis, and CRM integration.

## 🔹 Features

- **Real-time Audio Processing**: Upload and process audio files with automatic transcription
- **AI-Powered Summarization**: GPT-4 integration for intelligent call summaries
- **Sentiment Analysis**: Real-time sentiment tracking and analysis
- **Speaker Identification**: Automatic agent/customer speaker tagging
- **WebSocket Support**: Real-time updates for live call monitoring
- **CRM Integration**: Mock integration with Salesforce, Zendesk, and HubSpot
- **Analytics Dashboard**: Comprehensive call analytics and reporting
- **MongoDB Storage**: Scalable database for call data and analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (or use Docker Compose)
- OpenAI API Key
- FFmpeg (for audio processing)

### Installation

1. **Clone and setup**:
```bash
cd backend
cp .env.example .env
```

2. **Configure environment variables** in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_call_summarization
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
PORT=8000
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Setup (Recommended)

1. **Start with Docker Compose**:
```bash
# Make sure to set OPENAI_API_KEY in your environment
export OPENAI_API_KEY=your_api_key_here
docker-compose up -d
```

2. **Check service health**:
```bash
curl http://localhost:8000/health
```

## 📡 API Endpoints

### Call Management
- `POST /api/calls/start` - Start a new call session
- `POST /api/calls/{session_id}/audio` - Upload audio for processing
- `POST /api/calls/{session_id}/end` - End a call session
- `GET /api/calls/{session_id}/summary` - Get call summary and analytics

### Data Retrieval
- `GET /api/calls/history` - Get call history with pagination
- `GET /api/calls/search?q={query}` - Search calls by content
- `GET /api/analytics/dashboard` - Get analytics dashboard data

### System
- `GET /health` - Health check endpoint
- `GET /` - API information

## 🔌 WebSocket Events

The system supports real-time communication via Socket.IO:

### Client Events
- `join_call_session` - Join a call session room
- `leave_call_session` - Leave a call session room
- `request_session_status` - Get session status

### Server Events
- `transcript_update` - Real-time transcript updates
- `summary_update` - Summary generation updates
- `call_status` - Call status changes
- `audio_processing_status` - Audio processing progress
- `real_time_insights` - AI insights for agents

## 🗃️ Database Schema

### Collections

#### `calls`
```json
{
  "session_id": "unique-session-id",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T00:10:00Z",
  "status": "ended",
  "dialog_turns": [...],
  "audio_file_path": "/path/to/audio.wav",
  "metadata": {}
}
```

#### `summaries`
```json
{
  "call_session_id": "session-id",
  "summary_text": "Call summary...",
  "key_points": ["point1", "point2"],
  "sentiment_analysis": {...},
  "talk_time_stats": {...},
  "is_final": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `analytics`
```json
{
  "call_session_id": "session-id",
  "total_duration": 600.0,
  "agent_talk_time": 300.0,
  "customer_talk_time": 250.0,
  "silence_time": 50.0,
  "interruptions_count": 3,
  "overall_sentiment": "positive",
  "sentiment_scores": {...},
  "word_count": 150,
  "topics": ["billing", "support"]
}
```

## 🤖 AI Services

### Speech-to-Text
- **Provider**: OpenAI Whisper API
- **Features**: High-accuracy transcription with timestamps
- **Supported Formats**: WAV, MP3, M4A, FLAC, etc.

### Summarization & Analysis
- **Provider**: OpenAI GPT-4
- **Features**: 
  - Intelligent call summarization
  - Key points extraction
  - Sentiment analysis
  - Speaker identification
  - Real-time insights generation

### Audio Processing
- **Library**: librosa, pydub
- **Features**:
  - Audio format conversion
  - Quality enhancement
  - Speech/silence detection
  - Audio property analysis

## 🔗 CRM Integration

Mock CRM integration supporting:
- **Salesforce**: Activity logging and task creation
- **Zendesk**: Ticket updates and customer profile sync
- **HubSpot**: Call logging and contact updates

### CRM Features
- Automatic call summary sync
- Follow-up task creation
- Customer profile updates
- Analytics data export

## 📊 Analytics & Reporting

The system provides comprehensive analytics:
- Call duration and talk time ratios
- Sentiment analysis trends
- Topic classification
- Agent performance metrics
- Customer satisfaction scoring

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── models/          # Pydantic models
│   ├── services/        # Core business logic
│   │   ├── ai_service.py
│   │   ├── audio_processor.py
│   │   ├── socket_handler.py
│   │   ├── database.py
│   │   └── crm_mock.py
│   └── main.py          # FastAPI application
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Key Services
- **AIService**: OpenAI integration for transcription and summarization
- **AudioProcessor**: Audio file processing and analysis
- **SocketHandler**: WebSocket event management
- **DatabaseManager**: MongoDB operations
- **MockCRMIntegration**: CRM system simulation

## 🔧 Configuration

Environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `CORS_ORIGINS`: Allowed CORS origins
- `PORT`: Server port (default: 8000)

## 🧪 Testing

### Basic API Test
```bash
# Start a call
curl -X POST "http://localhost:8000/api/calls/start" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-1"}'

# Check health
curl http://localhost:8000/health
```

### WebSocket Test
Connect to `ws://localhost:8000/socket.io/` and emit:
```javascript
socket.emit('join_call_session', {session_id: 'test-session-1'});
```

## 📝 License

This project is part of a hackathon demonstration.

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include logging for debugging
4. Update documentation for new features

## 🚀 Deployment

### Production Considerations
- Use a production MongoDB instance (MongoDB Atlas recommended)
- Set up proper logging and monitoring
- Configure SSL/HTTPS
- Implement rate limiting
- Add authentication middleware
- Use environment-specific configurations

### Scaling
- Use Redis for session management
- Implement queue system for audio processing
- Add load balancing for multiple instances
- Consider using cloud storage for audio files
