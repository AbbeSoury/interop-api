# src/adapters/hl7_adapter.py
from typing import Dict, Any
import hl7
from datetime import datetime

class HL7Adapter:
    def parse(self, raw_message: str) -> Dict[str, Any]:
        """Parse un message HL7"""
        try:
            parsed = hl7.parse(raw_message)
            
            return {
                "message_type": str(parsed.segment('MSH')[9]),
                "patient": {
                    "id": str(parsed.segment('PID')[3]),
                    "name": {
                        "family": str(parsed.segment('PID')[5][0]),
                        "given": str(parsed.segment('PID')[5][1])
                    },
                    "dob": str(parsed.segment('PID')[7]),
                    "gender": str(parsed.segment('PID')[8])
                },
                "raw": str(parsed)
            }
        except Exception as e:
            raise ValueError(f"Invalid HL7 message: {str(e)}")
    
    def to_internal(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Conversion vers format interne"""
        return {
            "resource_type": "Patient",
            "identifier": message["patient"]["id"],
            "name": message["patient"]["name"],
            "birth_date": message["patient"]["dob"],
            "gender": message["patient"]["gender"],
            "meta": {
                "source": "HL7",
                "message_type": message["message_type"]
            }
        }
