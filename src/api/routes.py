from fastapi import FastAPI, HTTPException
from .models import MessageRequest, TransformationResponse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hl7
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Healthcare Gateway API",
    description="HL7 to FHIR message transformation API",
    version="1.0.0"
)

def format_datetime(dt_string: str) -> str:
    """
    Convertit une date/heure HL7 en format ISO8601
    Format HL7 attendu: YYYYMMDDHHMM
    """
    try:
        if dt_string == 'NaN':
            return None
        year = dt_string[0:4]
        month = dt_string[4:6]
        day = dt_string[6:8]
        hour = dt_string[8:10]
        minute = dt_string[10:12] if len(dt_string) > 10 else "00"
        return f"{year}-{month}-{day}T{hour}:{minute}:00"
    except Exception as e:
        logger.error(f"Error formatting datetime {dt_string}: {str(e)}")
        return None

def parse_hl7(message: str) -> Dict[str, Any]:
    """Parse un message HL7 en structure de données"""
    try:
        # Nettoyage et normalisation du message
        segments = [seg.strip() for seg in message.split('\n') if seg.strip()]
        result = {}
        
        logger.info(f"Found {len(segments)} segments:")
        for seg in segments:
            logger.info(f"Segment: {seg}")
        
        # Parse MSH
        msh = segments[0].split('|')
        result["message_type"] = msh[9]    # Type de message
        result["message_id"] = msh[10]     # ID du message (corrigé: index 10)
        result["datetime"] = msh[6]        # Date/heure du message
        
        # Parse les autres segments
        for segment in segments:
            fields = segment.split('|')
            segment_type = fields[0]
            logger.info(f"Processing segment type: {segment_type} with {len(fields)} fields")

            if segment_type == 'SCH':
                logger.info(f"Processing SCH segment: {segment}")
                try:
                    appointment_parts = fields[2].split('^') if len(fields) > 2 and fields[2] else ['', '']
                    service_parts = fields[6].split('^') if len(fields) > 6 and fields[6] else ['', '']
                    datetime_parts = fields[11].split('^') if len(fields) > 11 and fields[11] else ['', '', '', '']
                    creator_id = fields[-2].split('^')[0] if len(fields) > 26 else ''  # ID du créateur
                    creator_name = fields[-2].split('^')[1] if len(fields) > 26 and len(fields[-2].split('^')) > 1 else ''
                    
                    result["scheduling"] = {
                        "appointment_id": appointment_parts[0].strip(),
                        "service": {
                            "code": service_parts[0].strip(),
                            "name": service_parts[1].strip() if len(service_parts) > 1 else ""
                        },
                        "duration": datetime_parts[2].strip() if datetime_parts[2] != 'NaN' else "30",  # Durée par défaut si NaN
                        "start_datetime": datetime_parts[3].strip() if len(datetime_parts) > 3 else "",
                        "creator": {
                            "id": creator_id.strip(),
                            "name": creator_name.strip()
                        },
                        "status": "booked"  # Statut par défaut
                    }
                    logger.info(f"Parsed scheduling data: {result['scheduling']}")
                except Exception as e:
                    logger.error(f"Error parsing SCH segment: {str(e)}")

            elif segment_type == 'AIG':
                logger.info(f"Processing AIG segment: {segment}")
                try:
                    if len(fields) > 3:
                        agenda_name = fields[3].strip()
                        result["agenda"] = {
                            "id": agenda_name,
                            "name": agenda_name,
                            "display": agenda_name
                        }
                        logger.info(f"Parsed agenda data: {result['agenda']}")
                except Exception as e:
                    logger.error(f"Error parsing AIG segment: {str(e)}")

            elif segment_type == 'AIL':
                logger.info(f"Processing AIL segment: {segment}")
                try:
                    if len(fields) > 2:
                        location_id = fields[2].strip()
                        result["location"] = {
                            "id": location_id,
                            "display": f"Salle {location_id}"
                        }
                        logger.info(f"Parsed location data: {result['location']}")
                except Exception as e:
                    logger.error(f"Error parsing AIL segment: {str(e)}")

            elif segment_type == 'PID':
                logger.info(f"Processing PID segment: {segment}")
                try:
                    id_parts = fields[3].split('^')
                    name_parts = fields[5].split('^')
                    result["patient"] = {
                        "id": id_parts[0].strip(),
                        "name": {
                            "family": name_parts[0].strip(),
                            "given": name_parts[1].strip() if len(name_parts) > 1 else None
                        },
                        "birthDate": fields[7].strip() if len(fields) > 7 else None,
                        "gender": fields[8].strip() if len(fields) > 8 else None
                    }
                    logger.info(f"Parsed patient data: {result['patient']}")
                except Exception as e:
                    logger.error(f"Error parsing PID segment: {str(e)}")

        return result

    except Exception as e:
        logger.error(f"Error parsing HL7: {str(e)}")
        raise ValueError(f"HL7 parsing error: {str(e)}")

def hl7_to_fhir(parsed_hl7: Dict[str, Any]) -> Dict[str, Any]:
    """Convertit les données HL7 parsées en FHIR"""
    logger.info("Starting FHIR conversion")
    
    # Vérification des données requises
    if not parsed_hl7.get("scheduling", {}).get("appointment_id"):
        raise ValueError("Missing required appointment ID")
    
    fhir_resource = {
        "resourceType": "Bundle",
        "type": "collection",
        "id": parsed_hl7["message_id"],
        "timestamp": format_datetime(parsed_hl7["datetime"]),
        "entry": [
            {
                "resource": {
                    "resourceType": "Appointment",
                    "id": parsed_hl7["scheduling"]["appointment_id"],
                    "identifier": [
                        {
                            "system": "Doctolib",
                            "value": parsed_hl7["scheduling"]["appointment_id"]
                        }
                    ],
                    "status": "booked",
                    "serviceType": [
                        {
                            "coding": [
                                {
                                    "code": parsed_hl7["scheduling"]["service"]["code"],
                                    "display": parsed_hl7["scheduling"]["service"]["name"]
                                }
                            ],
                            "text": parsed_hl7.get("agenda", {}).get("name", "")
                        }
                    ],
                    "start": format_datetime(parsed_hl7["scheduling"]["start_datetime"]),
                    "minutesDuration": int(parsed_hl7["scheduling"]["duration"]),
                    "participant": [],
                    "created": format_datetime(parsed_hl7["datetime"]),
                    "extension": [
                        {
                            "url": "http://doctolib.com/fhir/StructureDefinition/agenda",
                            "valueString": parsed_hl7.get("agenda", {}).get("name", "")
                        }
                    ]
                }
            }
        ]
    }

    appointment = fhir_resource["entry"][0]["resource"]

    # Ajout des participants
    # Patient
    if parsed_hl7.get("patient"):
        appointment["participant"].append({
            "actor": {
                "reference": f"Patient/{parsed_hl7['patient']['id']}",
                "display": f"{parsed_hl7['patient']['name']['family']}, {parsed_hl7['patient']['name']['given']}"
            },
            "status": "accepted",
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "ATND"}]}]
        })

    # Agenda (Organization)
    if parsed_hl7.get("agenda", {}).get("name"):
        appointment["participant"].append({
            "actor": {
                "reference": f"Organization/{parsed_hl7['agenda']['id']}",
                "display": parsed_hl7['agenda']['name']
            },
            "status": "accepted",
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "PPRF"}]}]
        })

    # Créateur
    if parsed_hl7["scheduling"].get("creator", {}).get("id"):
        appointment["participant"].append({
            "actor": {
                "reference": f"User/{parsed_hl7['scheduling']['creator']['id']}",
                "display": parsed_hl7['scheduling']['creator']['name']
            },
            "status": "accepted",
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "REF"}]}]
        })

    # Location
    if parsed_hl7.get("location"):
        appointment["participant"].append({
            "actor": {
                "reference": f"Location/{parsed_hl7['location']['id']}",
                "display": parsed_hl7['location']['display']
            },
            "status": "accepted",
            "type": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": "LOC"}]}]
        })

    return fhir_resource

@app.post("/transform", response_model=TransformationResponse)
async def transform_message(request: MessageRequest):
    """Endpoint de transformation de messages"""
    try:
        if request.source_format == "HL7" and request.target_format == "FHIR":
            if isinstance(request.message, str):
                parsed_hl7 = parse_hl7(request.message)
                fhir_result = hl7_to_fhir(parsed_hl7)
                
                return {
                    "status": "success",
                    "data": fhir_result,
                    "metadata": {
                        "source_format": "HL7",
                        "target_format": "FHIR",
                        "timestamp": datetime.utcnow().isoformat(),
                        "parsed_segments": list(parsed_hl7.keys())
                    }
                }
            else:
                raise ValueError("HL7 message must be a string")
        
        raise NotImplementedError(f"Transformation from {request.source_format} to {request.target_format} not implemented yet")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de contrôle de santé"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
