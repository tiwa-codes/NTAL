"""USSD session state management using Redis."""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from .config import settings
from .redis_client import get_redis


class USSDSession:
    """Manage USSD session state in Redis."""
    
    SESSION_TTL = 300  # 5 minutes
    RATE_LIMIT_TTL = 86400  # 24 hours
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.key = f"ussd:session:{session_id}"
    
    async def get_state(self) -> Dict[str, Any]:
        """Get current session state."""
        redis_client = await get_redis()
        data = await redis_client.get(self.key)
        if data:
            return json.loads(data)
        return {
            "step": "consent",
            "language": "en",
            "responses": {}
        }
    
    async def set_state(self, state: Dict[str, Any]):
        """Save session state with TTL."""
        redis_client = await get_redis()
        await redis_client.setex(
            self.key,
            self.SESSION_TTL,
            json.dumps(state)
        )
    
    async def clear(self):
        """Clear session data."""
        redis_client = await get_redis()
        await redis_client.delete(self.key)
    
    @staticmethod
    async def check_rate_limit(msisdn_hash: str) -> bool:
        """
        Check if MSISDN has exceeded rate limit.
        
        Returns:
            True if under limit, False if exceeded
        """
        redis_client = await get_redis()
        key = f"ussd:rate:{msisdn_hash}"
        count = await redis_client.get(key)
        
        if count is None:
            # First request, set counter
            await redis_client.setex(key, USSDSession.RATE_LIMIT_TTL, "1")
            return True
        
        count_int = int(count)
        if count_int >= settings.RATE_LIMIT_MAX:
            return False
        
        # Increment counter
        await redis_client.incr(key)
        return True
    
    @staticmethod
    async def get_rate_limit_count(msisdn_hash: str) -> int:
        """Get current rate limit count for MSISDN."""
        redis_client = await get_redis()
        key = f"ussd:rate:{msisdn_hash}"
        count = await redis_client.get(key)
        return int(count) if count else 0
