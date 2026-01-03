from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socketio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from contextlib import asynccontextmanager

from .models.call_models import (
    StartCallRequest, StartCallResponse, EndCallRequest,
    CallSession, CallSummary, CallAnalytics, CallStatus,
    TranscriptUpdate, SummaryUpdate, DialogTurn, SpeakerType
)
from .services.ai_service import AIService
from .services.audio_processor import AudioProcessor
from .services.socket_handler import SocketHandler
from .services.database import DatabaseManager
from .services.crm_mock import MockCRMIntegration, CRMProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db_manager: Optional[DatabaseManager] = None
ai_service: Optional[AIService] = None
audio_processor: Optional[AudioProcessor] = None
socket_handler: Optional[SocketHandler] = None
crm_integration: Optional[MockCRMIntegration] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


# Create FastAPI app
app = FastAPI(
    title="AI Call Summarization API",
    description="Real-time call transcription, summarization, and CRM integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO
socket_handler = SocketHandler()
socket_app = socketio.ASGIApp(socket_handler.sio, app)


async def startup_event():
    """Initialize services on startup"""
    global db_manager, ai_service, audio_processor, crm_integration
    
    try:
        # Initialize database
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "ai_call_summarization")
        db_manager = DatabaseManager(mongodb_url, database_name)
        await db_manager.connect()
        
        # Initialize AI service
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found. AI features will be limited.")
            ai_service = None
        else:
            ai_service = AIService(openai_api_key)
        
        # Initialize audio processor
        audio_processor = AudioProcessor()
        
        # Initialize CRM integration
        crm_integration = MockCRMIntegration(CRMProvider.SALESFORCE)
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


async def shutdown_event():
    """Cleanup on shutdown"""
    global db_manager
    
    if db_manager:
        await db_manager.disconnect()
    
    logger.info("Application shutdown complete")


def get_services():
    """Dependency injection for services"""
    return {
        "db": db_manager,
        "ai": ai_service,
        "audio": audio_processor,
        "socket": socket_handler,
        "crm": crm_integration
    }


# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Call Summarization API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    services_status = {
        "database": db_manager is not None,
        "ai_service": ai_service is not None,
        "audio_processor": audio_processor is not None,
        "socket_handler": socket_handler is not None,
        "crm_integration": crm_integration is not None
    }
    
    all_healthy = all(services_status.values())
    
    return {
        "status": "healthy" if all_healthy else "partial",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/calls/start", response_model=StartCallResponse)
async def start_call(request: StartCallRequest, services: dict = Depends(get_services)):
    """Start a new call session"""
    try:
        # Create new call session
        call_session = CallSession(
            session_id=request.session_id,
            start_time=datetime.now(),
            status=CallStatus.ACTIVE,
            metadata=request.metadata or {}
        )
        
        # Save to database
        call_id = await services["db"].create_call_session(call_session)
        
        # Broadcast call status
        await services["socket"].broadcast_call_status(
            request.session_id, 
            "started",
            {"call_id": call_id}
        )
        
        logger.info(f"Started call session: {request.session_id}")
        
        return StartCallResponse(
            call_id=call_id,
            session_id=request.session_id,
            status="started",
            message="Call session started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error starting call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calls/{session_id}/audio")
async def upload_audio(
    session_id: str,
    audio_file: UploadFile = File(...),
    services: dict = Depends(get_services)
):
    """Upload audio file during call (processing happens on call end)"""
    try:
        # Validate call session exists
        call_session = await services["db"].get_call_session(session_id)
        if not call_session:
            raise HTTPException(status_code=404, detail="Call session not found")
        
        # Check if call is still active
        if call_session.status != CallStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Cannot upload audio to ended call")
        
        # Save uploaded file
        file_content = await audio_file.read()
        filename = f"{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio_file.filename}"
        audio_path = await services["audio"].save_uploaded_audio(file_content, filename)
        
        # Store audio file path in session (can handle multiple files)
        audio_files = call_session.metadata.get("audio_files", [])
        audio_files.append({
            "path": audio_path,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "size": len(file_content)
        })
        
        # Update the metadata properly
        updated_metadata = call_session.metadata.copy()
        updated_metadata["audio_files"] = audio_files
        
        await services["db"].update_call_session(session_id, {
            "metadata": updated_metadata,
            "audio_file_path": audio_path  # Keep latest for backward compatibility
        })
        
        # Broadcast upload status
        await services["socket"].broadcast_audio_processing_status(
            session_id, "uploaded", len(audio_files)
        )
        
        logger.info(f"Audio uploaded for session {session_id}: {filename}")
        
        return {
            "message": "Audio uploaded successfully. Processing will start when call ends.",
            "session_id": session_id,
            "filename": filename,
            "status": "uploaded",
            "files_count": len(audio_files)
        }
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error uploading audio: {error_details}")
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(e)}")


async def process_call_audio_after_end(session_id: str, audio_files: list, services: dict):
    """Background task to process all audio files after call ends"""
    try:
        logger.info(f"Starting post-call processing for session {session_id} with {len(audio_files)} files")
        
        # Update processing status
        await services["socket"].broadcast_audio_processing_status(session_id, "processing", 0.1)
        
        # Collect all transcript text as one continuous block
        complete_transcript = ""
        total_duration = 0
        combined_audio_props = {}
        
        # Process each audio file
        for i, audio_file in enumerate(audio_files):
            audio_path = audio_file["path"]
            
            # Update progress
            progress = 0.1 + (i / len(audio_files)) * 0.6  # 0.1 to 0.7 for processing files
            await services["socket"].broadcast_audio_processing_status(
                session_id, f"processing_file_{i+1}_of_{len(audio_files)}", progress
            )
            
            # Convert and enhance audio
            wav_path = services["audio"].convert_to_wav(audio_path)
            enhanced_path = services["audio"].enhance_audio_quality(wav_path)
            
            # Analyze audio properties
            audio_props = services["audio"].analyze_audio_properties(enhanced_path)
            total_duration += audio_props.get("duration", 0)
            
            if services["ai"]:
                # Transcribe audio with timestamps
                transcript_data = await services["ai"].transcribe_audio_with_timestamps(enhanced_path)
                
                # Extract just the text from all segments and combine
                file_transcript = " ".join([
                    segment["text"].strip() 
                    for segment in transcript_data.get("segments", [])
                    if segment["text"].strip()
                ])
                
                if file_transcript:
                    complete_transcript += f" {file_transcript}"
                    
                    # Broadcast a single transcript update for this file
                    transcript_update = TranscriptUpdate(
                        session_id=session_id,
                        timestamp=datetime.now(),
                        speaker=SpeakerType.AGENT,  # Generic speaker since we're not doing turn analysis
                        text=file_transcript,
                        confidence=transcript_data.get("confidence", 0.8),
                        is_final=True
                    )
                    
                    await services["socket"].broadcast_transcript_update(transcript_update)
            
            # Clean up temporary files for this audio file
            temp_files = [wav_path, enhanced_path]
            await services["audio"].cleanup_temp_files(temp_files)
        
        # Generate summary from complete transcript
        await services["socket"].broadcast_audio_processing_status(session_id, "generating_summary", 0.8)
        
        if services["ai"] and complete_transcript.strip():
            # Generate comprehensive summary from the complete transcript
            summary_data = await services["ai"].generate_summary_from_text(complete_transcript.strip(), is_final=True)
            
            # Create and save summary
            call_summary = CallSummary(
                call_session_id=session_id,
                summary_text=summary_data.get("summary", ""),
                key_points=summary_data.get("key_points", []),
                sentiment_analysis=summary_data,
                talk_time_stats={
                    "total_duration": total_duration,
                    "files_processed": len(audio_files),
                    "transcript_length": len(complete_transcript.strip())
                },
                created_at=datetime.now(),
                is_final=True
            )
            
            await services["db"].create_call_summary(call_summary)
            
            # Broadcast summary update
            summary_update = SummaryUpdate(
                session_id=session_id,
                summary_text=call_summary.summary_text,
                key_points=call_summary.key_points,
                is_final=True,
                sentiment_analysis=summary_data
            )
            
            await services["socket"].broadcast_summary_update(summary_update)
            
            # Create analytics based on complete transcript
            # Ensure sentiment values match Pydantic model validation
            customer_satisfaction = summary_data.get("customer_satisfaction", "neutral")
            if customer_satisfaction not in ["positive", "negative", "neutral"]:
                customer_satisfaction = "neutral"
            
            sentiment_analysis = summary_data.get("sentiment_analysis", {})
            if not isinstance(sentiment_analysis, dict):
                sentiment_analysis = {}
            
            call_analytics = CallAnalytics(
                call_session_id=session_id,
                total_duration=total_duration,
                agent_talk_time=total_duration * 0.6,  # Estimated split
                customer_talk_time=total_duration * 0.4,  # Estimated split
                silence_time=0,  # Simplified for now
                interruptions_count=0,  # Would need more sophisticated analysis
                overall_sentiment=customer_satisfaction,
                sentiment_scores=sentiment_analysis,
                word_count=len(complete_transcript.split()),
                topics=summary_data.get("topics", []),
                created_at=datetime.now()
            )
            
            await services["db"].create_call_analytics(call_analytics)
            
            # Sync to CRM
            await services["socket"].broadcast_audio_processing_status(session_id, "syncing_crm", 0.9)
            crm_result = await services["crm"].sync_call_summary(call_summary)
            logger.info(f"CRM sync result: {crm_result}")
        
        # Update call session status to completed
        await services["db"].update_call_session(session_id, {"status": "ended"})
        await services["socket"].broadcast_audio_processing_status(session_id, "completed", 1.0)
        await services["socket"].broadcast_call_status(session_id, "completed", {
            "total_files_processed": len(audio_files),
            "transcript_word_count": len(complete_transcript.split()),
            "total_duration": total_duration
        })
        
        logger.info(f"Post-call processing completed for session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error in post-call processing: {e}")
        await services["socket"].broadcast_audio_processing_status(session_id, "error", 0.0)
        await services["db"].update_call_session(session_id, {"status": "ended"})


@app.post("/api/calls/{session_id}/end")
async def end_call(
    session_id: str,
    request: EndCallRequest,
    background_tasks: BackgroundTasks,
    services: dict = Depends(get_services)
):
    """End a call session and trigger audio processing"""
    try:
        # Validate call session exists
        call_session = await services["db"].get_call_session(session_id)
        if not call_session:
            raise HTTPException(status_code=404, detail="Call session not found")
        
        # End the call session
        success = await services["db"].end_call_session(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end call session")
        
        # Broadcast call status
        await services["socket"].broadcast_call_status(session_id, "ended")
        
        # Get uploaded audio files
        audio_files = call_session.metadata.get("audio_files", [])
        
        response = {
            "message": "Call session ended successfully",
            "session_id": session_id,
            "status": "ended",
            "audio_files_count": len(audio_files)
        }
        
        # Start processing uploaded audio files in background
        if audio_files and services["ai"]:
            logger.info(f"Starting post-call processing for {len(audio_files)} audio files")
            
            # Update status to processing
            await services["db"].update_call_session(session_id, {"status": "processing"})
            await services["socket"].broadcast_call_status(session_id, "processing", {
                "stage": "starting_transcription",
                "files_to_process": len(audio_files)
            })
            
            # Process all audio files
            background_tasks.add_task(
                process_call_audio_after_end,
                session_id,
                audio_files,
                services
            )
            
            response["processing_status"] = "Audio processing started"
        elif not audio_files:
            response["processing_status"] = "No audio files to process"
        else:
            response["processing_status"] = "AI service not available"
        
        logger.info(f"Call session ended: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls/{session_id}/summary")
async def get_call_summary(session_id: str, services: dict = Depends(get_services)):
    """Get call summary"""
    try:
        # Get final summary
        final_summary = await services["db"].get_final_summary(session_id)
        if not final_summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        # Get analytics
        analytics = await services["db"].get_call_analytics(session_id)
        
        # Get CRM sync status
        crm_status = await services["crm"].get_sync_status(session_id)
        
        return {
            "summary": final_summary.model_dump(),
            "analytics": analytics.model_dump() if analytics else None,
            "crm_status": crm_status
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls/history")
async def get_call_history(
    limit: int = 50,
    skip: int = 0,
    services: dict = Depends(get_services)
):
    """Get call history"""
    try:
        history = await services["db"].get_call_history(limit, skip)
        return {
            "calls": history,
            "total": len(history),
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error getting call history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard(services: dict = Depends(get_services)):
    """Get analytics dashboard data"""
    try:
        # Get recent analytics (last 30 days)
        end_date = datetime.now()
        start_date = datetime.now().replace(day=1)  # Start of month
        
        analytics_summary = await services["db"].get_analytics_summary(start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": analytics_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calls/search")
async def search_calls(
    q: str,
    limit: int = 20,
    services: dict = Depends(get_services)
):
    """Search calls by content"""
    try:
        results = await services["db"].search_calls(q, limit)
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount the Socket.IO app
app.mount("/socket.io/", socket_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
