import openai
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from ..models.call_models import DialogTurn, SpeakerType, SentimentType

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def transcribe_audio_with_timestamps(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio with detailed timestamps using OpenAI Whisper API"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )
            return transcript.model_dump()
        except Exception as e:
            logger.error(f"Error transcribing audio with timestamps: {e}")
            raise
    
    async def identify_speakers(self, dialog_turns: List[str]) -> List[DialogTurn]:
        """Use LLM to identify speakers in conversation turns"""
        try:
            prompt = f"""
            Analyze the following conversation and identify who is speaking in each turn - Agent or Customer.
            An Agent is typically professional, helpful, and represents the company.
            A Customer is typically asking questions, making requests, or expressing concerns.
            
            Conversation:
            {chr(10).join([f"{i+1}. {turn}" for i, turn in enumerate(dialog_turns)])}
            
            Return a JSON array where each element has:
            - "turn_number": number (1-indexed)
            - "speaker": "agent" or "customer"
            - "confidence": float between 0-1
            
            Example response:
            [
                {{"turn_number": 1, "speaker": "agent", "confidence": 0.9}},
                {{"turn_number": 2, "speaker": "customer", "confidence": 0.8}}
            ]
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            speaker_analysis = json.loads(response.choices[0].message.content)
            
            # Convert to DialogTurn objects
            result = []
            for i, (turn_text, analysis) in enumerate(zip(dialog_turns, speaker_analysis)):
                speaker = SpeakerType.AGENT if analysis["speaker"] == "agent" else SpeakerType.CUSTOMER
                result.append(DialogTurn(
                    timestamp=datetime.now(),
                    speaker=speaker,
                    text=turn_text,
                    confidence=analysis["confidence"]
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error identifying speakers: {e}")
            # Fallback: alternate between agent and customer
            result = []
            for i, turn_text in enumerate(dialog_turns):
                speaker = SpeakerType.AGENT if i % 2 == 0 else SpeakerType.CUSTOMER
                result.append(DialogTurn(
                    timestamp=datetime.now(),
                    speaker=speaker,
                    text=turn_text,
                    confidence=0.5
                ))
            return result
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using GPT-4"""
        try:
            prompt = f"""
            Analyze the sentiment of the following text and provide:
            1. Overall sentiment: positive, negative, or neutral
            2. Confidence score (0-1)
            3. Emotional tone (e.g., frustrated, satisfied, curious, etc.)
            4. Key emotional indicators from the text
            
            Text: "{text}"
            
            Return JSON format:
            {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.0-1.0,
                "emotional_tone": "description",
                "key_indicators": ["indicator1", "indicator2"]
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotional_tone": "unknown",
                "key_indicators": []
            }
    
    async def generate_summary(self, dialog_turns: List[DialogTurn], is_final: bool = False) -> Dict[str, Any]:
        """Generate conversation summary using GPT-4"""
        try:
            # Format conversation for AI
            conversation_text = "\n".join([
                f"{turn.speaker.value.upper()}: {turn.text}"
                for turn in dialog_turns
            ])
            
            summary_type = "final" if is_final else "interim"
            
            prompt = f"""
            Analyze this customer service conversation and provide a comprehensive {summary_type} summary.
            
            Conversation:
            {conversation_text}
            
            Provide a JSON response with:
            1. "summary": A concise summary of the conversation
            2. "key_points": Array of important points discussed
            3. "action_items": Array of follow-up actions needed
            4. "resolution_status": "resolved", "pending", or "escalated"
            5. "customer_satisfaction": "high", "medium", "low", or "unknown"
            6. "topics": Array of main topics discussed
            7. "duration_assessment": Brief comment on call efficiency
            
            Example:
            {{
                "summary": "Customer called about billing issue...",
                "key_points": ["Billing discrepancy", "Account verification"],
                "action_items": ["Update billing system", "Send confirmation email"],
                "resolution_status": "resolved",
                "customer_satisfaction": "high",
                "topics": ["billing", "account management"],
                "duration_assessment": "Efficient resolution"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "summary": "Error generating summary",
                "key_points": [],
                "action_items": [],
                "resolution_status": "unknown",
                "customer_satisfaction": "unknown",
                "topics": [],
                "duration_assessment": "Unable to assess"
            }
    
    async def generate_summary_from_text(self, transcript_text: str, is_final: bool = False) -> Dict[str, Any]:
        """Generate conversation summary from complete transcript text using GPT-4"""
        try:
            summary_type = "final" if is_final else "interim"
            
            prompt = f"""
            You are analyzing a customer service call from a Zimbabwe call center. Extract actionable insights for call center optimization.
            
            CALL TRANSCRIPT:
            {transcript_text}
            
            Provide a JSON response with the following Zimbabwe call center insights:
            
            1. "summary": 3-bullet summary of key discussion points
            2. "sentiment": "positive", "neutral", or "negative" 
            3. "category": Classify the call type - "billing", "technical", "bundles", "complaints", "general_inquiry", or "other"
            4. "action_items": Specific follow-up actions needed by call center agents
            5. "customer_requests": What the customer specifically asked for
            6. "resolution_status": "resolved", "pending", or "escalated"
            7. "priority": "high", "medium", or "low" based on urgency
            8. "tags": Array of searchable tags (e.g., ["data_bundle", "payment_issue", "network_problem"])
            9. "agent_performance": Brief assessment of agent handling
            10. "follow_up_required": true/false if customer needs callback
            
            EXAMPLE OUTPUT:
            {{
                "summary": ["Customer reported network connectivity issues in Harare", "Agent provided troubleshooting steps", "Issue resolved with network reset"],
                "sentiment": "positive", 
                "category": "technical",
                "action_items": ["Monitor network stability in Harare area", "Update customer profile with resolution"],
                "customer_requests": ["Fix network connectivity", "Compensate for downtime"],
                "resolution_status": "resolved",
                "priority": "medium",
                "tags": ["network_issue", "harare", "connectivity", "resolved"],
                "agent_performance": "Good - provided clear troubleshooting steps and resolved issue efficiently",
                "follow_up_required": false
            }}
            
            Focus on insights that help Zimbabwe call centers improve service delivery and customer satisfaction.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating summary from text: {e}")
            return {
                "summary": "Error generating summary",
                "key_points": [],
                "action_items": [],
                "resolution_status": "unknown",
                "customer_satisfaction": "unknown",
                "topics": [],
                "sentiment_analysis": "Unable to analyze",
                "duration_assessment": "Unable to assess"
            }
    
    async def generate_real_time_insights(self, recent_turns: List[DialogTurn]) -> Dict[str, Any]:
        """Generate real-time insights during active call"""
        try:
            if len(recent_turns) < 3:
                return {"insights": [], "suggestions": []}
            
            recent_text = "\n".join([
                f"{turn.speaker.value.upper()}: {turn.text}"
                for turn in recent_turns[-5:]  # Last 5 turns
            ])
            
            prompt = f"""
            Analyze this recent conversation snippet and provide real-time insights for the agent.
            
            Recent conversation:
            {recent_text}
            
            Provide JSON response with:
            1. "insights": Array of observations about customer state/needs
            2. "suggestions": Array of helpful suggestions for the agent
            3. "urgency_level": "low", "medium", or "high"
            4. "customer_mood": Brief description
            
            Example:
            {{
                "insights": ["Customer seems frustrated with wait time", "Technical issue with login"],
                "suggestions": ["Acknowledge wait time", "Offer screen sharing for tech support"],
                "urgency_level": "medium",
                "customer_mood": "slightly frustrated but cooperative"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating real-time insights: {e}")
            return {
                "insights": [],
                "suggestions": [],
                "urgency_level": "low",
                "customer_mood": "unknown"
            }
