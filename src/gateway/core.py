# src/gateway/core.py
from typing import Dict, Any
import logging
from datetime import datetime
from .config import GatewayConfig
from ..adapters import HL7Adapter, FHIRAdapter
from ..validators.message import MessageValidator

logger = logging.getLogger(__name__)

class HealthcareGateway:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.validator = MessageValidator()
        self.adapters = {
            'HL7': HL7Adapter(),
            'FHIR': FHIRAdapter()
        }
        
    async def process_message(
        self,
        message: Dict[str, Any],
        source_format: str,
        target_format: str
    ) -> Dict[str, Any]:
        """Traitement principal d'un message"""
        logger.info(f"Processing message: {source_format} -> {target_format}")
        
        try:
            # Validation du format source
            if source_format not in self.config.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported source format: {source_format}")
            
            # Validation du message
            self.validator.validate(message, source_format)
            
            # Obtention de l'adaptateur
            source_adapter = self.adapters[source_format]
            target_adapter = self.adapters[target_format]
            
            # Transformation
            internal_format = source_adapter.to_internal(message)
            transformed = target_adapter.from_internal(internal_format)
            
            # Création de la réponse
            return {
                "status": "success",
                "data": transformed,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "source_format": source_format,
                    "target_format": target_format,
                    "version": self.config.VERSION
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
