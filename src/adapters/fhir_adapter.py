# src/adapters/fhir_adapter.py
from typing import Dict, Any
import json
from datetime import datetime

class FHIRAdapter:
    def parse(self, raw_message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse un message FHIR"""
        try:
            if not isinstance(raw_message, dict):
                raw_message = json.loads(raw_message)
                
            if "resourceType" not in raw_message:
                raise ValueError("Invalid FHIR resource: missing resourceType")
                
            return raw_message
            
        except Exception as e:
            raise ValueError(f"Invalid FHIR message: {str(e)}")
    
    def to_internal(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Conversion vers format interne"""
        return {
            "resource_type": message["resourceType"],
            "identifier": message.get("identifier", [{}])[0].get("value"),
            "name": {
                "family": message.get("name", [{}])[0].get("family"),
                "given": message.get("name", [{}])[0].get("given", [])[0]
            },
            "birth_date": message.get("birthDate"),
            "gender": message.get("gender"),
            "meta": {
                "source": "FHIR",
                "version": "R4"
            }
        }
    