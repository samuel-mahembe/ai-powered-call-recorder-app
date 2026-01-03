#!/usr/bin/env python3
"""
Patch for AI Service to fix OpenAI empty response issue
"""

# This is the improved generate_summary_from_text function
# Copy this into your ai_service.py to replace the existing function

async def generate_summary_from_text(self, transcript_text: str, is_final: bool = False) -> Dict[str, Any]:
    """Generate conversation summary from complete transcript text using GPT-4"""
    try:
        summary_type = "final" if is_final else "interim"
        
        # Truncate transcript if too long to avoid OpenAI issues
        max_transcript_length = 8000  # Leave room for prompt
        if len(transcript_text) > max_transcript_length:
            transcript_text = transcript_text[:max_transcript_length] + "... [truncated]"
            logger.warning(f"Transcript truncated to {max_transcript_length} characters")
        
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
        IMPORTANT: Respond ONLY with valid JSON. Do not include any explanatory text before or after the JSON.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000  # Limit response size
        )
        
        # Get the raw response content
        raw_content = response.choices[0].message.content
        
        # Debug logging
        logger.info(f"OpenAI response length: {len(raw_content) if raw_content else 0}")
        
        # Handle empty response
        if not raw_content or raw_content.strip() == "":
            logger.error("OpenAI returned empty response")
            raise ValueError("Empty response from OpenAI")
        
        # Clean the response (remove any non-JSON text)
        raw_content = raw_content.strip()
        
        # Try to extract JSON if wrapped in markdown or other text
        if raw_content.startswith("```json"):
            # Extract JSON from markdown code block
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                raw_content = raw_content[start:end]
        elif raw_content.startswith("```"):
            # Extract JSON from generic code block
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            if start != -1 and end > start:
                raw_content = raw_content[start:end]
        
        # Parse JSON
        try:
            result = json.loads(raw_content)
            
            # Validate required fields and fix any issues
            if not isinstance(result.get("summary"), list):
                result["summary"] = [str(result.get("summary", "Unable to generate summary"))]
            
            if result.get("resolution_status") not in ["resolved", "pending", "escalated"]:
                result["resolution_status"] = "pending"
            
            if result.get("sentiment") not in ["positive", "neutral", "negative"]:
                result["sentiment"] = "neutral"
            
            if result.get("category") not in ["billing", "technical", "bundles", "complaints", "general_inquiry", "other"]:
                result["category"] = "other"
            
            if result.get("priority") not in ["high", "medium", "low"]:
                result["priority"] = "medium"
            
            # Ensure lists are actually lists
            for field in ["action_items", "customer_requests", "tags"]:
                if not isinstance(result.get(field), list):
                    result[field] = []
            
            # Ensure boolean fields are boolean
            if not isinstance(result.get("follow_up_required"), bool):
                result["follow_up_required"] = False
            
            return result
            
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing failed: {json_err}")
            logger.error(f"Raw content: {raw_content[:500]}...")
            raise ValueError(f"Invalid JSON from OpenAI: {json_err}")
        
    except Exception as e:
        logger.error(f"Error generating summary from text: {e}")
        return {
            "summary": ["Error generating summary"],
            "sentiment": "neutral",
            "category": "other",
            "action_items": ["Review call recording for manual analysis"],
            "customer_requests": ["Unable to determine from transcript"],
            "resolution_status": "pending",
            "priority": "medium",
            "tags": ["processing_error", "manual_review_needed"],
            "agent_performance": "Unable to assess due to processing error",
            "follow_up_required": True
        }
