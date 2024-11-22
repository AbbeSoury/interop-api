# src/gateway/config.py
from pydantic import BaseSettings
from typing import Dict, Any

class GatewayConfig(BaseSettings):
    """Configuration de la Gateway"""
    APP_NAME: str = "Healthcare Gateway"
    VERSION: str = "1.0.0"
    
    # Formats supportés
    SUPPORTED_FORMATS: Dict[str, str] = {
        "HL7": "2.5",
        "FHIR": "R4"
    }
    
    # Configuration des adaptateurs
    ADAPTER_CONFIG: Dict[str, Any] = {
        "HL7": {
            "default_version": "2.5",
            "encoding": "utf-8"
        },
        "FHIR": {
            "default_version": "R4",
            "validate_schema": True
        }
    }

    class Config:
        env_prefix = "GATEWAY_"
