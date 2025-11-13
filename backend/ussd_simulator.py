#!/usr/bin/env python3
"""
USSD Simulator for testing NTAL USSD flow.
Simulates requests from a USSD aggregator.
"""

import requests
import sys


class USSDSimulator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/ussd"
        self.session_id = None
        self.phone_number = None
        self.service_code = "*123#"
        self.text = ""
    
    def start_session(self, phone_number):
        """Start a new USSD session."""
        self.session_id = f"sim-{phone_number}"
        self.phone_number = phone_number
        self.text = ""
        
        print(f"\n{'='*60}")
        print(f"Starting USSD session for {phone_number}")
        print(f"Service Code: {self.service_code}")
        print(f"{'='*60}\n")
        
        response = self._send_request()
        return response
    
    def send_input(self, choice):
        """Send user choice to USSD."""
        if self.text:
            self.text += "*"
        self.text += str(choice)
        
        print(f"User input: {choice}")
        response = self._send_request()
        return response
    
    def _send_request(self):
        """Send request to USSD endpoint."""
        payload = {
            "sessionId": self.session_id,
            "phoneNumber": self.phone_number,
            "serviceCode": self.service_code,
            "text": self.text
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            
            data = response.json()
            ussd_response = data.get("response", "")
            
            # Parse response type and message
            response_type = ussd_response[:3]  # CON or END
            message = ussd_response[4:]  # Message after "CON " or "END "
            
            print(f"\n{'-'*60}")
            print(f"Response Type: {response_type}")
            print(f"{'-'*60}")
            print(message)
            print(f"{'-'*60}\n")
            
            return response_type, message
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "ERR", str(e)
    
    def run_interactive(self, phone_number):
        """Run interactive USSD session."""
        response_type, _ = self.start_session(phone_number)
        
        while response_type == "CON":
            try:
                choice = input("Enter your choice: ").strip()
                if not choice:
                    break
                response_type, _ = self.send_input(choice)
            except KeyboardInterrupt:
                print("\n\nSession cancelled.")
                break
        
        print("\n" + "="*60)
        print("Session ended.")
        print("="*60 + "\n")


def run_automated_scenario(simulator, phone, scenario_name, inputs):
    """Run an automated test scenario."""
    print(f"\n{'#'*60}")
    print(f"# Scenario: {scenario_name}")
    print(f"{'#'*60}")
    
    response_type, _ = simulator.start_session(phone)
    
    for choice in inputs:
        if response_type != "CON":
            break
        response_type, _ = simulator.send_input(choice)
    
    print(f"\n{'='*60}")
    print(f"Scenario '{scenario_name}' completed.")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("USSD Simulator for NTAL")
        print("\nUsage:")
        print("  python ussd_simulator.py interactive <phone_number>")
        print("  python ussd_simulator.py scenario <scenario_name>")
        print("\nAvailable scenarios:")
        print("  low_risk      - Complete flow with no serious symptoms")
        print("  emergency     - Emergency case with danger signs")
        print("  malaria       - Suspected malaria case")
        print("  callback      - Request callback after triage")
        sys.exit(1)
    
    mode = sys.argv[1]
    simulator = USSDSimulator()
    
    if mode == "interactive":
        phone = sys.argv[2] if len(sys.argv) > 2 else "+254712345678"
        simulator.run_interactive(phone)
    
    elif mode == "scenario":
        scenario = sys.argv[2] if len(sys.argv) > 2 else "low_risk"
        
        scenarios = {
            "low_risk": {
                "phone": "+254712111111",
                "name": "Low Risk - No Serious Symptoms",
                "inputs": ["1", "1", "3", "1", "2", "2", "2", "1", "2"]
                # Consent:Yes, Lang:EN, Age:18-49, Gender:Male, 
                # Fever:No, Headache:No, Danger:No, Cough:Yes, Callback:No
            },
            "emergency": {
                "phone": "+254712222222",
                "name": "Emergency - Danger Signs Present",
                "inputs": ["1", "1", "3", "2", "1", "1", "1", "2", "1"]
                # Consent:Yes, Lang:EN, Age:18-49, Gender:Female,
                # Fever:Yes, Headache:Yes, Danger:YES, Cough:No, Callback:Yes
            },
            "malaria": {
                "phone": "+254712333333",
                "name": "Possible Malaria - Fever + Severe Headache",
                "inputs": ["1", "1", "2", "1", "1", "1", "2", "2", "2"]
                # Consent:Yes, Lang:EN, Age:5-17, Gender:Male,
                # Fever:Yes, Headache:Yes, Danger:No, Cough:No, Callback:No
            },
            "callback": {
                "phone": "+254712444444",
                "name": "Request Callback After Triage",
                "inputs": ["1", "1", "3", "2", "1", "2", "2", "2", "1"]
                # Consent:Yes, Lang:EN, Age:18-49, Gender:Female,
                # Fever:Yes, Headache:No, Danger:No, Cough:No, Callback:Yes
            }
        }
        
        if scenario not in scenarios:
            print(f"Unknown scenario: {scenario}")
            print(f"Available: {', '.join(scenarios.keys())}")
            sys.exit(1)
        
        s = scenarios[scenario]
        run_automated_scenario(simulator, s["phone"], s["name"], s["inputs"])
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
