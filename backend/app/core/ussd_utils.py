"""Utilities for USSD operations."""

import hashlib
from .config import settings


def hash_msisdn(msisdn: str) -> str:
    """
    Hash MSISDN with pepper for privacy.
    
    Args:
        msisdn: Phone number to hash
        
    Returns:
        SHA-256 hash of msisdn + pepper
    """
    combined = f"{msisdn}{settings.HASH_PEPPER}"
    return hashlib.sha256(combined.encode()).hexdigest()


def mask_msisdn(msisdn: str) -> str:
    """
    Mask MSISDN for logging (show only last 2-3 digits).
    
    Args:
        msisdn: Phone number to mask
        
    Returns:
        Masked phone number (e.g., "***567")
    """
    if len(msisdn) < 3:
        return "***"
    return f"***{msisdn[-3:]}"
