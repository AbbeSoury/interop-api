from pydantic import BaseModel
from typing import Dict, Any, Union

class MessageRequest(BaseModel):
    message: Union[str, Dict[str, Any]]  # Peut être string (HL7) ou dict (FHIR)
    source_format: str
    target_format: str

class TransformationResponse(BaseModel):
    status: str
    data: Union[str, Dict[str, Any]]  # Peut être string (HL7) ou dict (FHIR)
    metadata: Dict[str, Any]
