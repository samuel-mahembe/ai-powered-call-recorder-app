import socketio
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from ..models.call_models import TranscriptUpdate, SummaryUpdate, DialogTurn, SpeakerType

logger = logging.getLogger(__name__)


class SocketHandler:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )
        self.active_sessions: Dict[str, Dict] = {}
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            logger.info(f"Client connected: {sid}")
            await self.sio.emit('connection_status', {
                'status': 'connected',
                'message': 'Successfully connected to AI Call Summarization service'
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")
            # Clean up any active sessions for this client
            await self.cleanup_client_sessions(sid)
        
        @self.sio.event
        async def join_call_session(sid, data):
            """Join a specific call session room"""
            try:
                session_id = data.get('session_id')
                if not session_id:
                    await self.sio.emit('error', {
                        'message': 'session_id is required'
                    }, room=sid)
                    return
                
                # Join the session room
                await self.sio.enter_room(sid, f"call_{session_id}")
                
                # Track the session
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = {
                        'clients': [],
                        'start_time': datetime.now(),
                        'dialog_turns': [],
                        'status': 'active'
                    }
                
                self.active_sessions[session_id]['clients'].append(sid)
                
                await self.sio.emit('joined_session', {
                    'session_id': session_id,
                    'message': f'Joined call session {session_id}'
                }, room=sid)
                
                logger.info(f"Client {sid} joined session {session_id}")
                
            except Exception as e:
                logger.error(f"Error joining session: {e}")
                await self.sio.emit('error', {
                    'message': 'Failed to join session'
                }, room=sid)
        
        @self.sio.event
        async def leave_call_session(sid, data):
            """Leave a call session room"""
            try:
                session_id = data.get('session_id')
                if not session_id:
                    return
                
                await self.sio.leave_room(sid, f"call_{session_id}")
                
                # Remove client from session tracking
                if session_id in self.active_sessions:
                    if sid in self.active_sessions[session_id]['clients']:
                        self.active_sessions[session_id]['clients'].remove(sid)
                
                await self.sio.emit('left_session', {
                    'session_id': session_id
                }, room=sid)
                
                logger.info(f"Client {sid} left session {session_id}")
                
            except Exception as e:
                logger.error(f"Error leaving session: {e}")
        
        @self.sio.event
        async def request_session_status(sid, data):
            """Request current status of a call session"""
            try:
                session_id = data.get('session_id')
                if session_id in self.active_sessions:
                    session_data = self.active_sessions[session_id]
                    await self.sio.emit('session_status', {
                        'session_id': session_id,
                        'status': session_data['status'],
                        'start_time': session_data['start_time'].isoformat(),
                        'dialog_turns_count': len(session_data['dialog_turns']),
                        'clients_count': len(session_data['clients'])
                    }, room=sid)
                else:
                    await self.sio.emit('session_status', {
                        'session_id': session_id,
                        'status': 'not_found'
                    }, room=sid)
                    
            except Exception as e:
                logger.error(f"Error getting session status: {e}")
    
    async def broadcast_transcript_update(self, transcript_update: TranscriptUpdate):
        """Broadcast transcript update to all clients in the session"""
        try:
            room = f"call_{transcript_update.session_id}"
            
            # Update session data
            if transcript_update.session_id in self.active_sessions:
                dialog_turn = DialogTurn(
                    timestamp=transcript_update.timestamp,
                    speaker=transcript_update.speaker,
                    text=transcript_update.text,
                    confidence=transcript_update.confidence
                )
                self.active_sessions[transcript_update.session_id]['dialog_turns'].append(dialog_turn)
            
            # Broadcast to all clients in the room
            await self.sio.emit('transcript_update', {
                'session_id': transcript_update.session_id,
                'timestamp': transcript_update.timestamp.isoformat(),
                'speaker': transcript_update.speaker.value,
                'text': transcript_update.text,
                'confidence': transcript_update.confidence,
                'is_final': transcript_update.is_final
            }, room=room)
            
            logger.info(f"Broadcasted transcript update for session {transcript_update.session_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting transcript update: {e}")
    
    async def broadcast_summary_update(self, summary_update: SummaryUpdate):
        """Broadcast summary update to all clients in the session"""
        try:
            room = f"call_{summary_update.session_id}"
            
            await self.sio.emit('summary_update', {
                'session_id': summary_update.session_id,
                'summary_text': summary_update.summary_text,
                'key_points': summary_update.key_points,
                'is_final': summary_update.is_final,
                'sentiment_analysis': summary_update.sentiment_analysis,
                'timestamp': datetime.now().isoformat()
            }, room=room)
            
            logger.info(f"Broadcasted summary update for session {summary_update.session_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting summary update: {e}")
    
    async def broadcast_real_time_insights(self, session_id: str, insights: Dict):
        """Broadcast real-time insights to agents in the session"""
        try:
            room = f"call_{session_id}"
            
            await self.sio.emit('real_time_insights', {
                'session_id': session_id,
                'insights': insights.get('insights', []),
                'suggestions': insights.get('suggestions', []),
                'urgency_level': insights.get('urgency_level', 'low'),
                'customer_mood': insights.get('customer_mood', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }, room=room)
            
            logger.info(f"Broadcasted real-time insights for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting insights: {e}")
    
    async def broadcast_call_status(self, session_id: str, status: str, metadata: Optional[Dict] = None):
        """Broadcast call status changes"""
        try:
            room = f"call_{session_id}"
            
            # Update session status
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = status
            
            await self.sio.emit('call_status', {
                'session_id': session_id,
                'status': status,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }, room=room)
            
            logger.info(f"Broadcasted call status update for session {session_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error broadcasting call status: {e}")
    
    async def broadcast_audio_processing_status(self, session_id: str, stage: str, progress: float = 0.0):
        """Broadcast audio processing status updates"""
        try:
            room = f"call_{session_id}"
            
            await self.sio.emit('audio_processing_status', {
                'session_id': session_id,
                'stage': stage,  # e.g., 'uploading', 'processing', 'transcribing', 'analyzing'
                'progress': progress,  # 0.0 to 1.0
                'timestamp': datetime.now().isoformat()
            }, room=room)
            
        except Exception as e:
            logger.error(f"Error broadcasting audio processing status: {e}")
    
    async def cleanup_client_sessions(self, sid: str):
        """Clean up sessions when client disconnects"""
        try:
            # Remove client from all active sessions
            for session_id, session_data in self.active_sessions.items():
                if sid in session_data['clients']:
                    session_data['clients'].remove(sid)
                    
                    # If no clients left, mark session as inactive
                    if len(session_data['clients']) == 0:
                        session_data['status'] = 'inactive'
                        
                        # Optionally clean up old sessions
                        session_age = datetime.now() - session_data['start_time']
                        if session_age.total_seconds() > 3600:  # 1 hour
                            del self.active_sessions[session_id]
                            logger.info(f"Cleaned up old session: {session_id}")
                            
        except Exception as e:
            logger.error(f"Error cleaning up client sessions: {e}")
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Get statistics for a specific session"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        dialog_turns = session_data['dialog_turns']
        
        # Calculate basic stats
        agent_turns = [turn for turn in dialog_turns if turn.speaker == SpeakerType.AGENT]
        customer_turns = [turn for turn in dialog_turns if turn.speaker == SpeakerType.CUSTOMER]
        
        return {
            'session_id': session_id,
            'status': session_data['status'],
            'duration': (datetime.now() - session_data['start_time']).total_seconds(),
            'total_turns': len(dialog_turns),
            'agent_turns': len(agent_turns),
            'customer_turns': len(customer_turns),
            'active_clients': len(session_data['clients'])
        }
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return [session_id for session_id, data in self.active_sessions.items() 
                if data['status'] == 'active']
