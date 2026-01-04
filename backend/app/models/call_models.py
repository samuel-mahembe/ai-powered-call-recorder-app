from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# Enums
class CallStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    PROCESSING = "processing"
    COMPLETED = "completed"


class SpeakerType(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"
    SYSTEM = "system"


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Request/Response Models
class StartCallRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class StartCallResponse(BaseModel):
    call_id: str = Field(..., description="Database ID of the call")
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Call status")
    message: str = Field(..., description="Response message")


class EndCallRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for call end")


# Core Data Models
class DialogTurn(BaseModel):
    timestamp: datetime = Field(..., description="When this turn occurred")
    speaker: SpeakerType = Field(..., description="Who spoke")
    text: str = Field(..., description="What was said")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for transcription")


class CallSession(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    session_id: str = Field(..., description="Unique session identifier")
    start_time: datetime = Field(..., description="When the call started")
    end_time: Optional[datetime] = Field(None, description="When the call ended")
    status: CallStatus = Field(default=CallStatus.ACTIVE, description="Current call status")
    dialog_turns: List[DialogTurn] = Field(default_factory=list, description="Conversation turns")
    audio_file_path: Optional[str] = Field(None, description="Path to audio file")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {"populate_by_name": True}


class CallSummary(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    call_session_id: str = Field(..., description="Associated call session ID")
    summary_text: Any = Field(..., description="Summary text (can be string or list)")
    key_points: List[str] = Field(default_factory=list, description="Key points from the call")
    sentiment_analysis: Dict[str, Any] = Field(default_factory=dict, description="Sentiment analysis results")
    talk_time_stats: Dict[str, Any] = Field(default_factory=dict, description="Talk time statistics")
    created_at: datetime = Field(default_factory=datetime.now, description="When summary was created")
    is_final: bool = Field(default=False, description="Whether this is the final summary")

    model_config = {"populate_by_name": True}


class CallAnalytics(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    call_session_id: str = Field(..., description="Associated call session ID")
    total_duration: float = Field(..., ge=0, description="Total call duration in seconds")
    agent_talk_time: float = Field(..., ge=0, description="Agent talk time in seconds")
    customer_talk_time: float = Field(..., ge=0, description="Customer talk time in seconds")
    silence_time: float = Field(default=0.0, ge=0, description="Silence time in seconds")
    interruptions_count: int = Field(default=0, ge=0, description="Number of interruptions")
    overall_sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    sentiment_scores: Dict[str, Any] = Field(default_factory=dict, description="Detailed sentiment scores")
    word_count: int = Field(default=0, ge=0, description="Total word count")
    topics: List[str] = Field(default_factory=list, description="Identified topics")
    created_at: datetime = Field(default_factory=datetime.now, description="When analytics were created")

    model_config = {"populate_by_name": True}


# WebSocket Update Models
class TranscriptUpdate(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="When the transcript was generated")
    speaker: SpeakerType = Field(..., description="Who spoke")
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    is_final: bool = Field(default=False, description="Whether this is final or interim")


class SummaryUpdate(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    summary_text: Any = Field(..., description="Summary text (can be string or list)")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    is_final: bool = Field(default=False, description="Whether this is final summary")
    sentiment_analysis: Dict[str, Any] = Field(default_factory=dict, description="Sentiment analysis")

