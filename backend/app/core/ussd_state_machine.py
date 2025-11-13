"""USSD state machine for handling user flow."""

from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from .language_strings import get_message
from .triage_engine import assess_risk, get_priority_from_risk
from .ussd_utils import hash_msisdn
from .config import settings
from ..models.models import Encounter, Callback


class USSDStateMachine:
    """Handles USSD flow state transitions."""
    
    def __init__(self, language: str = "en"):
        self.language = language
    
    def process_step(
        self,
        step: str,
        user_input: str,
        state: Dict[str, Any],
        db: Session
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Process user input for current step.
        
        Args:
            step: Current step in the flow
            user_input: User's menu selection
            state: Current session state
            db: Database session
            
        Returns:
            Tuple of (response_type, message, new_state)
            response_type: "CON" for continue or "END" for end
        """
        
        if step == "consent":
            return self._handle_consent(user_input, state)
        
        elif step == "language":
            return self._handle_language(user_input, state)
        
        elif step == "age_group":
            return self._handle_age_group(user_input, state)
        
        elif step == "gender":
            return self._handle_gender(user_input, state)
        
        elif step == "fever":
            return self._handle_fever(user_input, state)
        
        elif step == "severe_headache":
            return self._handle_severe_headache(user_input, state)
        
        elif step == "danger_sign":
            return self._handle_danger_sign(user_input, state)
        
        elif step == "cough":
            return self._handle_cough(user_input, state)
        
        elif step == "result":
            return self._handle_result(user_input, state, db)
        
        else:
            return "END", get_message(self.language, "invalid_input"), state
    
    def _handle_consent(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle consent step."""
        if user_input == "1":
            state["responses"]["consent"] = True
            state["step"] = "language"
            return "CON", get_message(self.language, "language"), state
        elif user_input == "2":
            return "END", get_message(self.language, "consent_declined"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "consent"), state
    
    def _handle_language(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle language selection."""
        if user_input == "1":
            self.language = "en"
            state["language"] = "en"
        elif user_input == "2":
            self.language = "yo"
            state["language"] = "yo"
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "language"), state
        
        state["step"] = "age_group"
        return "CON", get_message(self.language, "age_group"), state
    
    def _handle_age_group(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle age group selection."""
        age_map = {"1": "<5", "2": "5-17", "3": "18-49", "4": "50+"}
        if user_input in age_map:
            state["responses"]["age_group"] = age_map[user_input]
            state["step"] = "gender"
            return "CON", get_message(self.language, "gender"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "age_group"), state
    
    def _handle_gender(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle gender selection."""
        gender_map = {"1": "male", "2": "female", "3": "other"}
        if user_input in gender_map:
            state["responses"]["gender"] = gender_map[user_input]
            state["step"] = "fever"
            return "CON", get_message(self.language, "fever"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "gender"), state
    
    def _handle_fever(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle fever symptom."""
        if user_input in ["1", "2"]:
            state["responses"]["fever"] = (user_input == "1")
            state["step"] = "severe_headache"
            return "CON", get_message(self.language, "severe_headache"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "fever"), state
    
    def _handle_severe_headache(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle severe headache symptom."""
        if user_input in ["1", "2"]:
            state["responses"]["severe_headache"] = (user_input == "1")
            state["step"] = "danger_sign"
            return "CON", get_message(self.language, "danger_sign"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "severe_headache"), state
    
    def _handle_danger_sign(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle danger sign symptom."""
        if user_input in ["1", "2"]:
            state["responses"]["danger_sign"] = (user_input == "1")
            state["step"] = "cough"
            return "CON", get_message(self.language, "cough"), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "danger_sign"), state
    
    def _handle_cough(self, user_input: str, state: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle cough symptom and perform triage."""
        if user_input in ["1", "2"]:
            state["responses"]["cough"] = (user_input == "1")
            
            # Perform triage assessment
            symptoms = {
                "fever": state["responses"].get("fever", False),
                "severe_headache": state["responses"].get("severe_headache", False),
                "danger_sign": state["responses"].get("danger_sign", False),
                "cough": state["responses"].get("cough", False)
            }
            
            risk_code, advice, urgent_flag = assess_risk(symptoms)
            state["responses"]["risk_code"] = risk_code
            state["responses"]["advice"] = advice
            state["responses"]["urgent_flag"] = urgent_flag
            
            # Show result based on risk
            result_key = risk_code.lower()
            state["step"] = "result"
            return "CON", get_message(self.language, result_key), state
        else:
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, "cough"), state
    
    def _handle_result(self, user_input: str, state: Dict[str, Any], db: Session) -> Tuple[str, str, Dict[str, Any]]:
        """Handle callback request and save encounter."""
        if user_input == "1":
            # User wants callback - save encounter and create callback
            self._save_encounter_and_callback(state, db)
            return "END", get_message(self.language, "callback_queued"), state
        elif user_input == "2":
            # No callback needed - just save encounter
            self._save_encounter(state, db)
            return "END", get_message(self.language, "goodbye"), state
        else:
            risk_code = state["responses"].get("risk_code", "LOW_RISK")
            result_key = risk_code.lower()
            return "CON", get_message(self.language, "invalid_input") + "\n\n" + get_message(self.language, result_key), state
    
    def _save_encounter(self, state: Dict[str, Any], db: Session) -> Encounter:
        """Save encounter to database."""
        responses = state.get("responses", {})
        msisdn = state.get("msisdn", "")
        
        encounter = Encounter(
            channel="USSD",
            msisdn_hash=hash_msisdn(msisdn),
            age_group=responses.get("age_group"),
            patient_gender=responses.get("gender"),
            symptoms_json=responses,
            risk_code=responses.get("risk_code"),
            consent_given=responses.get("consent", False),
            consent_version=settings.CONSENT_VERSION,
            status="pending",
            urgency="critical" if responses.get("urgent_flag") else "medium"
        )
        
        db.add(encounter)
        db.commit()
        db.refresh(encounter)
        return encounter
    
    def _save_encounter_and_callback(self, state: Dict[str, Any], db: Session):
        """Save encounter and create callback request."""
        encounter = self._save_encounter(state, db)
        
        # Create callback
        responses = state.get("responses", {})
        msisdn = state.get("msisdn", "")
        risk_code = responses.get("risk_code", "LOW_RISK")
        
        callback = Callback(
            encounter_id=encounter.id,
            msisdn_hash=hash_msisdn(msisdn),
            priority=get_priority_from_risk(risk_code),
            status="queued"
        )
        
        db.add(callback)
        db.commit()
