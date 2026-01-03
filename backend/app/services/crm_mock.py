import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
from enum import Enum
from ..models.call_models import CallSummary, CallAnalytics

logger = logging.getLogger(__name__)


class CRMProvider(str, Enum):
    SALESFORCE = "salesforce"
    ZENDESK = "zendesk"
    HUBSPOT = "hubspot"


class CRMStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class MockCRMIntegration:
    """Mock CRM integration that simulates API calls to popular CRM systems"""
    
    def __init__(self, provider: CRMProvider = CRMProvider.SALESFORCE):
        self.provider = provider
        self.api_delay = 1.0  # Simulate API delay
        self.success_rate = 0.9  # 90% success rate for demo
        self.synced_records: Dict[str, Dict] = {}
        
    async def sync_call_summary(self, call_summary: CallSummary, 
                               customer_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Sync call summary to CRM system"""
        try:
            logger.info(f"Syncing call summary to {self.provider.value} CRM...")
            
            # Simulate API delay
            await asyncio.sleep(self.api_delay)
            
            # Create CRM record
            crm_record = self._create_crm_record(call_summary, customer_info)
            
            # Simulate success/failure
            import random
            if random.random() < self.success_rate:
                # Success
                record_id = str(uuid.uuid4())
                self.synced_records[call_summary.call_session_id] = {
                    "crm_record_id": record_id,
                    "provider": self.provider.value,
                    "status": CRMStatus.SUCCESS,
                    "synced_at": datetime.now(),
                    "record_data": crm_record
                }
                
                return {
                    "status": CRMStatus.SUCCESS,
                    "crm_record_id": record_id,
                    "provider": self.provider.value,
                    "message": f"Successfully synced to {self.provider.value}",
                    "synced_at": datetime.now().isoformat()
                }
            else:
                # Failure
                error_msg = self._generate_mock_error()
                logger.warning(f"CRM sync failed: {error_msg}")
                
                return {
                    "status": CRMStatus.FAILED,
                    "provider": self.provider.value,
                    "error": error_msg,
                    "retry_available": True
                }
                
        except Exception as e:
            logger.error(f"Error syncing to CRM: {e}")
            return {
                "status": CRMStatus.FAILED,
                "provider": self.provider.value,
                "error": str(e),
                "retry_available": True
            }
    
    async def sync_call_analytics(self, call_analytics: CallAnalytics) -> Dict[str, Any]:
        """Sync call analytics to CRM system"""
        try:
            logger.info(f"Syncing call analytics to {self.provider.value} CRM...")
            
            await asyncio.sleep(self.api_delay * 0.5)  # Faster for analytics
            
            # Create analytics record
            analytics_record = self._create_analytics_record(call_analytics)
            
            # Simulate success
            import random
            if random.random() < 0.95:  # Higher success rate for analytics
                record_id = str(uuid.uuid4())
                
                return {
                    "status": CRMStatus.SUCCESS,
                    "analytics_record_id": record_id,
                    "provider": self.provider.value,
                    "message": f"Analytics synced to {self.provider.value}",
                    "synced_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": CRMStatus.FAILED,
                    "provider": self.provider.value,
                    "error": "Analytics sync temporarily unavailable"
                }
                
        except Exception as e:
            logger.error(f"Error syncing analytics to CRM: {e}")
            return {
                "status": CRMStatus.FAILED,
                "provider": self.provider.value,
                "error": str(e)
            }
    
    async def create_follow_up_task(self, call_session_id: str, 
                                   summary: str, action_items: List[str]) -> Dict[str, Any]:
        """Create follow-up tasks in CRM system"""
        try:
            logger.info(f"Creating follow-up tasks in {self.provider.value} CRM...")
            
            await asyncio.sleep(self.api_delay * 0.8)
            
            tasks = []
            for i, action_item in enumerate(action_items):
                task_id = str(uuid.uuid4())
                task = {
                    "task_id": task_id,
                    "title": action_item,
                    "description": f"Follow-up from call session {call_session_id}",
                    "priority": "medium",
                    "due_date": (datetime.now()).strftime("%Y-%m-%d"),
                    "status": "open",
                    "created_at": datetime.now().isoformat()
                }
                tasks.append(task)
            
            return {
                "status": CRMStatus.SUCCESS,
                "provider": self.provider.value,
                "tasks_created": len(tasks),
                "tasks": tasks,
                "message": f"Created {len(tasks)} follow-up tasks"
            }
            
        except Exception as e:
            logger.error(f"Error creating follow-up tasks: {e}")
            return {
                "status": CRMStatus.FAILED,
                "provider": self.provider.value,
                "error": str(e)
            }
    
    async def update_customer_profile(self, customer_id: str, 
                                     call_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer profile with call insights"""
        try:
            logger.info(f"Updating customer profile in {self.provider.value} CRM...")
            
            await asyncio.sleep(self.api_delay * 0.6)
            
            # Mock customer profile update
            profile_updates = {
                "last_call_date": datetime.now().isoformat(),
                "call_sentiment": call_insights.get("customer_satisfaction", "unknown"),
                "interaction_count": 1,  # Would be incremented in real system
                "notes": f"Call summary: {call_insights.get('summary', '')[:100]}...",
                "tags": call_insights.get("topics", [])
            }
            
            return {
                "status": CRMStatus.SUCCESS,
                "provider": self.provider.value,
                "customer_id": customer_id,
                "updates_applied": profile_updates,
                "message": "Customer profile updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating customer profile: {e}")
            return {
                "status": CRMStatus.FAILED,
                "provider": self.provider.value,
                "error": str(e)
            }
    
    def _create_crm_record(self, call_summary: CallSummary, 
                          customer_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Create CRM record structure based on provider"""
        base_record = {
            "call_session_id": call_summary.call_session_id,
            "summary": call_summary.summary_text,
            "key_points": call_summary.key_points,
            "sentiment": call_summary.sentiment_analysis,
            "talk_time_stats": call_summary.talk_time_stats,
            "created_at": call_summary.created_at.isoformat(),
            "is_final": call_summary.is_final
        }
        
        if self.provider == CRMProvider.SALESFORCE:
            return {
                "Subject": f"Call Summary - {call_summary.call_session_id}",
                "Description": call_summary.summary_text,
                "Status": "Completed",
                "Type": "Call",
                "CallDurationInSeconds": call_summary.talk_time_stats.get("total_duration", 0),
                "CallObject": "Log",
                **base_record
            }
        elif self.provider == CRMProvider.ZENDESK:
            return {
                "type": "call",
                "subject": f"Call Summary - {call_summary.call_session_id}",
                "comment": {
                    "body": call_summary.summary_text,
                    "public": False
                },
                "custom_fields": [
                    {"id": "call_duration", "value": call_summary.talk_time_stats.get("total_duration", 0)},
                    {"id": "sentiment", "value": call_summary.sentiment_analysis.get("overall", "neutral")}
                ],
                **base_record
            }
        elif self.provider == CRMProvider.HUBSPOT:
            return {
                "properties": {
                    "hs_timestamp": call_summary.created_at.isoformat(),
                    "hs_call_title": f"Call Summary - {call_summary.call_session_id}",
                    "hs_call_body": call_summary.summary_text,
                    "hs_call_status": "COMPLETED",
                    "hs_call_duration": call_summary.talk_time_stats.get("total_duration", 0)
                },
                **base_record
            }
        
        return base_record
    
    def _create_analytics_record(self, call_analytics: CallAnalytics) -> Dict[str, Any]:
        """Create analytics record for CRM"""
        return {
            "call_session_id": call_analytics.call_session_id,
            "total_duration": call_analytics.total_duration,
            "agent_talk_time": call_analytics.agent_talk_time,
            "customer_talk_time": call_analytics.customer_talk_time,
            "silence_time": call_analytics.silence_time,
            "interruptions": call_analytics.interruptions_count,
            "overall_sentiment": call_analytics.overall_sentiment.value,
            "sentiment_scores": call_analytics.sentiment_scores,
            "word_count": call_analytics.word_count,
            "topics": call_analytics.topics,
            "performance_metrics": {
                "talk_ratio": call_analytics.agent_talk_time / call_analytics.total_duration if call_analytics.total_duration > 0 else 0,
                "response_efficiency": 1 - (call_analytics.silence_time / call_analytics.total_duration) if call_analytics.total_duration > 0 else 0,
                "engagement_score": min(1.0, call_analytics.word_count / 100)  # Simple engagement metric
            }
        }
    
    def _generate_mock_error(self) -> str:
        """Generate realistic CRM error messages"""
        errors = [
            "API rate limit exceeded. Please try again later.",
            "Invalid authentication credentials.",
            "Required field 'AccountId' is missing.",
            "Network timeout while connecting to CRM service.",
            "Insufficient permissions to create records.",
            "CRM service temporarily unavailable.",
            "Data validation failed: Invalid date format.",
            "Duplicate record detected."
        ]
        import random
        return random.choice(errors)
    
    async def get_sync_status(self, call_session_id: str) -> Dict[str, Any]:
        """Get synchronization status for a call session"""
        if call_session_id in self.synced_records:
            record = self.synced_records[call_session_id]
            return {
                "call_session_id": call_session_id,
                "status": record["status"],
                "provider": record["provider"],
                "crm_record_id": record.get("crm_record_id"),
                "synced_at": record["synced_at"].isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        else:
            return {
                "call_session_id": call_session_id,
                "status": "not_synced",
                "provider": self.provider.value
            }
    
    async def retry_sync(self, call_session_id: str) -> Dict[str, Any]:
        """Retry failed synchronization"""
        logger.info(f"Retrying CRM sync for session {call_session_id}")
        
        # Simulate retry with higher success rate
        await asyncio.sleep(self.api_delay * 0.5)
        
        import random
        if random.random() < 0.8:  # 80% success on retry
            record_id = str(uuid.uuid4())
            self.synced_records[call_session_id] = {
                "crm_record_id": record_id,
                "provider": self.provider.value,
                "status": CRMStatus.SUCCESS,
                "synced_at": datetime.now(),
                "retry_count": 1
            }
            
            return {
                "status": CRMStatus.SUCCESS,
                "crm_record_id": record_id,
                "message": "Retry successful"
            }
        else:
            return {
                "status": CRMStatus.FAILED,
                "message": "Retry failed - manual intervention required"
            }
