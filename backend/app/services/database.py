from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.call_models import CallSession, CallSummary, CallAnalytics

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, mongodb_url: str, database_name: str):
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Indexes for calls collection
            await self.db.calls.create_index("session_id", unique=True)
            await self.db.calls.create_index("start_time")
            await self.db.calls.create_index("status")
            
            # Indexes for summaries collection
            await self.db.summaries.create_index("call_session_id")
            await self.db.summaries.create_index("created_at")
            await self.db.summaries.create_index("is_final")
            
            # Indexes for analytics collection
            await self.db.analytics.create_index("call_session_id", unique=True)
            await self.db.analytics.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    # Call Session Operations
    async def create_call_session(self, call_session: CallSession) -> str:
        """Create a new call session"""
        try:
            # Convert to dict and exclude None _id to let MongoDB auto-generate
            call_data = call_session.model_dump(by_alias=True, exclude_none=True)
            if '_id' in call_data and call_data['_id'] is None:
                del call_data['_id']
            
            result = await self.db.calls.insert_one(call_data)
            logger.info(f"Created call session: {call_session.session_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating call session: {e}")
            raise
    
    async def get_call_session(self, session_id: str) -> Optional[CallSession]:
        """Get call session by session_id"""
        try:
            doc = await self.db.calls.find_one({"session_id": session_id})
            if doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                return CallSession(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting call session: {e}")
            return None
    
    async def update_call_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update call session"""
        try:
            result = await self.db.calls.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating call session: {e}")
            return False
    
    async def add_dialog_turn(self, session_id: str, dialog_turn: Dict[str, Any]) -> bool:
        """Add dialog turn to call session"""
        try:
            result = await self.db.calls.update_one(
                {"session_id": session_id},
                {"$push": {"dialog_turns": dialog_turn}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding dialog turn: {e}")
            return False
    
    async def end_call_session(self, session_id: str) -> bool:
        """End call session"""
        try:
            result = await self.db.calls.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": "ended",
                        "end_time": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error ending call session: {e}")
            return False
    
    # Call Summary Operations
    async def create_call_summary(self, call_summary: CallSummary) -> str:
        """Create call summary"""
        try:
            summary_data = call_summary.model_dump(by_alias=True, exclude_none=True)
            if '_id' in summary_data and summary_data['_id'] is None:
                del summary_data['_id']
            result = await self.db.summaries.insert_one(summary_data)
            logger.info(f"Created call summary for session: {call_summary.call_session_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating call summary: {e}")
            raise
    
    async def get_call_summaries(self, call_session_id: str) -> List[CallSummary]:
        """Get all summaries for a call session"""
        try:
            cursor = self.db.summaries.find({"call_session_id": call_session_id}).sort("created_at", -1)
            docs = await cursor.to_list(length=None)
            # Convert ObjectId to string for each document
            for doc in docs:
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
            return [CallSummary(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting call summaries: {e}")
            return []
    
    async def get_final_summary(self, call_session_id: str) -> Optional[CallSummary]:
        """Get final summary for a call session"""
        try:
            doc = await self.db.summaries.find_one({
                "call_session_id": call_session_id,
                "is_final": True
            })
            if doc:
                # Convert ObjectId to string for Pydantic compatibility
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
                return CallSummary(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting final summary: {e}")
            return None
    
    # Call Analytics Operations
    async def create_call_analytics(self, call_analytics: CallAnalytics) -> str:
        """Create call analytics"""
        try:
            analytics_data = call_analytics.model_dump(by_alias=True, exclude_none=True)
            # Exclude _id if it's None to avoid duplicate key errors
            if '_id' in analytics_data and analytics_data['_id'] is None:
                del analytics_data['_id']
            result = await self.db.analytics.insert_one(analytics_data)
            logger.info(f"Created call analytics for session: {call_analytics.call_session_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating call analytics: {e}")
            raise
    
    async def get_call_analytics(self, call_session_id: str) -> Optional[CallAnalytics]:
        """Get call analytics"""
        try:
            doc = await self.db.analytics.find_one({"call_session_id": call_session_id})
            if doc:
                return CallAnalytics(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting call analytics: {e}")
            return None
    
    # History and Reporting
    async def get_call_history(self, limit: int = 50, skip: int = 0) -> List[CallSession]:
        """Get paginated call history"""
        try:
            cursor = self.db.calls.find().sort("start_time", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=None)
            # Convert ObjectId to string for each document
            for doc in docs:
                if "_id" in doc and doc["_id"]:
                    doc["_id"] = str(doc["_id"])
            return [CallSession(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting call history: {e}")
            return []
    
    async def get_analytics_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics summary for a date range"""
        try:
            pipeline = [
                {
                    "$match": {
                        "start_time": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "analytics",
                        "localField": "session_id",
                        "foreignField": "call_session_id",
                        "as": "analytics"
                    }
                },
                {
                    "$unwind": {
                        "path": "$analytics",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_calls": {"$sum": 1},
                        "avg_duration": {"$avg": "$analytics.total_duration"},
                        "avg_agent_talk_time": {"$avg": "$analytics.agent_talk_time"},
                        "avg_customer_talk_time": {"$avg": "$analytics.customer_talk_time"},
                        "total_interruptions": {"$sum": "$analytics.interruptions_count"},
                        "sentiment_distribution": {
                            "$push": "$analytics.overall_sentiment"
                        }
                    }
                }
            ]
            
            cursor = self.db.calls.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                return result[0]
            else:
                return {
                    "total_calls": 0,
                    "avg_duration": 0,
                    "avg_agent_talk_time": 0,
                    "avg_customer_talk_time": 0,
                    "total_interruptions": 0,
                    "sentiment_distribution": []
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    async def search_calls(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search calls by text content"""
        try:
            # Create text search index if not exists
            try:
                await self.db.calls.create_index([("dialog_turns.text", "text")])
            except:
                pass  # Index might already exist
            
            cursor = self.db.calls.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Error searching calls: {e}")
            return []
