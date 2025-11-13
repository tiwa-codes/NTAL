"""Triage engine for symptom assessment and risk stratification."""

from typing import Dict, Tuple


def assess_risk(symptoms: Dict[str, bool]) -> Tuple[str, str, bool]:
    """
    Assess risk level based on symptoms.
    
    Args:
        symptoms: Dictionary of symptom keys to boolean values
        
    Returns:
        Tuple of (risk_code, advice, urgent_flag)
    """
    danger_sign = symptoms.get("danger_sign", False)
    fever = symptoms.get("fever", False)
    severe_headache = symptoms.get("severe_headache", False)
    cough = symptoms.get("cough", False)
    
    # Emergency: Any danger sign
    if danger_sign:
        return (
            "EMERGENCY",
            "Emergency: nearest clinic now.",
            True
        )
    
    # Malaria suspect: Fever + severe headache
    if fever and severe_headache:
        return (
            "MALARIA_SUSPECT",
            "Possible malaria: visit PHC soon.",
            False
        )
    
    # General fever
    if fever:
        return (
            "FEVER_GENERAL",
            "Monitor; visit PHC if persists.",
            False
        )
    
    # Low risk: No significant symptoms
    return (
        "LOW_RISK",
        "Low risk. Rest and monitor.",
        False
    )


def get_priority_from_risk(risk_code: str) -> str:
    """Map risk code to callback priority."""
    priority_map = {
        "EMERGENCY": "urgent",
        "MALARIA_SUSPECT": "high",
        "FEVER_GENERAL": "medium",
        "LOW_RISK": "low"
    }
    return priority_map.get(risk_code, "medium")
