"""
SMS Adapter - Stub for SMS integration
This adapter will handle SMS-based triage submissions
"""

class SMSAdapter:
    """Adapter for SMS integration"""
    
    def __init__(self):
        self.provider = None  # Will be configured with SMS gateway provider
    
    async def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Send SMS message
        
        Args:
            phone_number: Recipient phone number
            message: SMS message text
        
        Returns:
            dict with status and message_id
        """
        # Stub implementation
        return {
            "status": "sent",
            "message_id": "stub-message-id",
            "phone_number": phone_number
        }
    
    async def receive_sms(self, phone_number: str, message: str) -> dict:
        """
        Process incoming SMS
        
        Args:
            phone_number: Sender's phone number
            message: SMS message text
        
        Returns:
            dict with parsed triage data
        """
        # Stub implementation - parse SMS keywords
        return {
            "phone_number": phone_number,
            "message": message,
            "parsed": False
        }
    
    async def send_confirmation(self, phone_number: str, encounter_id: int) -> dict:
        """Send triage confirmation SMS"""
        message = f"Thank you for using NTAL Telehealth. Your case ID is {encounter_id}."
        return await self.send_sms(phone_number, message)
