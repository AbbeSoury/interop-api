# src/validators/message.py
from typing import Dict, Any
import json
from datetime import datetime

class MessageValidator:
    def validate(self, message: Dict[str, Any], format_type: str) -> bool:
        """Valide un message selon son format"""
        if format_type == "HL7":
            return self._validate_hl7(message)
        elif format_type == "FHIR":
            return self._validate_fhir(message)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _validate_hl7(self, message: Dict[str, Any]) -> bool:
        """Validation spécifique HL7"""
        required_fields = ["message_type", "patient"]
        
        if not all(field in message for field in required_fields):
            raise ValueError("Missing required HL7 fields")
            
        return True
    
    def _validate_fhir(self, message: Dict[str, Any]) -> bool:
        """Validation spécifique FHIR"""
        if "resourceType" not in message:
            raise ValueError("Missing resourceType in FHIR message")
            
        return True
