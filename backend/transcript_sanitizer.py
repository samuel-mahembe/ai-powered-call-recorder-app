#!/usr/bin/env python3
"""
Transcript sanitization utility to remove sensitive information before OpenAI processing
"""
import re
import logging

logger = logging.getLogger(__name__)

class TranscriptSanitizer:
    """Sanitizes call center transcripts by removing/masking sensitive information"""
    
    def __init__(self):
        # Patterns for sensitive information
        self.phone_patterns = [
            r'\b0\d{9}\b',  # Zimbabwe phone numbers (0788405008)
            r'\b\d{3}\s\d{3}\s\d{3}\b',  # Spaced phone numbers (078 840 5008)
            r'\b\d{4}\s\d{3}\s\d{3}\b',  # Alternative spacing (0788 405 008)
        ]
        
        self.amount_patterns = [
            r'\b\d+\s*(Zig|ZWL|USD|Dollar|Dollars)\b',  # Amount with currency
            r'\b(Zig|ZWL|USD|Dollar|Dollars)\s*\d+\b',  # Currency with amount
            r'\$\d+',  # Dollar amounts
        ]
        
        self.name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b',  # Full names (3 parts)
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Two-part names
        ]
        
        # Account/reference number patterns
        self.account_patterns = [
            r'\b\d{8,12}\b',  # Account numbers
            r'\b[A-Z]{2}\d{6,10}\b',  # Reference codes
        ]
    
    def sanitize(self, transcript: str) -> str:
        """
        Sanitize transcript by removing/masking sensitive information
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Sanitized transcript with sensitive info masked
        """
        original_length = len(transcript)
        sanitized = transcript
        
        # Mask phone numbers
        for pattern in self.phone_patterns:
            sanitized = re.sub(pattern, '[PHONE_NUMBER]', sanitized, flags=re.IGNORECASE)
        
        # Mask amounts and currency
        for pattern in self.amount_patterns:
            sanitized = re.sub(pattern, '[AMOUNT]', sanitized, flags=re.IGNORECASE)
        
        # Mask names (but preserve agent names mentioned in greeting)
        # Skip first occurrence which is usually agent introduction
        name_matches = []
        for pattern in self.name_patterns:
            matches = list(re.finditer(pattern, sanitized))
            if len(matches) > 1:  # Keep first (agent), mask others (customers)
                for match in matches[1:]:
                    sanitized = sanitized[:match.start()] + '[CUSTOMER_NAME]' + sanitized[match.end():]
        
        # Mask account numbers
        for pattern in self.account_patterns:
            sanitized = re.sub(pattern, '[ACCOUNT_NUMBER]', sanitized)
        
        # Log sanitization stats
        changes = original_length - len(sanitized) + sanitized.count('[')
        if changes > 0:
            logger.info(f"Sanitized transcript: {changes} sensitive items masked")
        
        return sanitized
    
    def structure_transcript(self, transcript: str) -> str:
        """
        Add basic structure to transcript by identifying speaker changes
        
        Args:
            transcript: Sanitized transcript text
            
        Returns:
            Structured transcript with speaker labels
        """
        # Simple heuristic: sentences starting with greetings/responses are likely speaker changes
        speaker_indicators = [
            r'\b(Good morning|Good afternoon|Hello|Hi|Thank you|Thanks|Okay|Oh|Sure|Yes|No)\b',
            r'\b(May I|Can I|Could you|Would you|Let me|I can|I will|I need|I have)\b',
        ]
        
        sentences = re.split(r'[.!?]+', transcript)
        structured_lines = []
        current_speaker = "Agent"  # Assume first speaker is agent
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Simple speaker detection based on content patterns
            if i == 0:
                # First sentence is usually agent greeting
                structured_lines.append(f"Agent: {sentence}")
            elif any(re.search(pattern, sentence, re.IGNORECASE) for pattern in speaker_indicators):
                # Likely speaker change
                current_speaker = "Customer" if current_speaker == "Agent" else "Agent"
                structured_lines.append(f"{current_speaker}: {sentence}")
            else:
                # Continue with same speaker
                structured_lines.append(f"{current_speaker}: {sentence}")
        
        return "\n".join(structured_lines)

# Test the sanitizer
if __name__ == "__main__":
    sanitizer = TranscriptSanitizer()
    
    test_transcript = """Good afternoon, thank you for calling EcoCash support, my name is Fadzai, how can I help you today? Hi Fadzai, I just tried to buy airtime using EcoCash, the money was deducted from my wallet but I haven't received my airtime. Oh I'm sorry to hear that happened, let me look into it right away, may I have the number you tried to use and the exact amount you purchased? Sure, the number is 0788 405 008 and I tried to buy 500 Zig worth of airtime about 10 minutes ago. Oh thank you, for security could you please share your phone number and your full name? My number is 0788 405 008 and my full name is Grace Muno Kwan. Great thank you, please hold for a moment while I put up the transaction. I can see the debit of Zig 500 at 1507 today, it looks like the airtime did not post to the mobile operator system, I apologise for the inconvenience. Okay so what happened now, I really need the airtime. Oh that's okay, let me just do the airtime credit right now. Hi Grace, the airtime has been credited to your wallet, thank you so much for calling EcoCash support, would you need any further assistance? No, that's all, thanks. Ah thank you, have a good day."""
    
    print("Original transcript:")
    print(test_transcript)
    print("\n" + "="*50 + "\n")
    
    sanitized = sanitizer.sanitize(test_transcript)
    print("Sanitized transcript:")
    print(sanitized)
    print("\n" + "="*50 + "\n")
    
    structured = sanitizer.structure_transcript(sanitized)
    print("Structured transcript:")
    print(structured)
