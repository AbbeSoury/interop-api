import streamlit as st
import requests
import json
from datetime import datetime

def get_hl7_example():
    return """MSH|^~\&|LABO|CH|SIH|CH|20240319103025||OML^O33^OML_O33|123456|P|2.5
PID|1||12345^^^IPP^PI||DOE^JOHN^^^^^L||19700101|M|||1 RUE DE LA PAIX^^PARIS^^75001^FRA^H||0123456789^^^john.doe@email.com
PV1|1|O|CARDIO||||DR SMITH^JANE^^^^^MD|||||||||||V123456
ORC|NW|123456||||||^^^20240319103025^^R
OBR|1|123456||CBC^HEMOGRAMME^LN||20240319103025|20240319103025|||||||20240319103025||DR SMITH^JANE^^^^^MD|0123456789|||||||||F
SAC|1|||10^mL|SANG||||||20240319103025"""

def get_fhir_example():
    return json.dumps({
        "resourceType": "ServiceRequest",
        "id": "123456",
        "status": "active",
        "intent": "order",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "58410-2",
                "display": "CBC panel - Blood"
            }]
        },
        "subject": {
            "reference": "Patient/12345",
            "display": "DOE, John"
        }
    }, indent=2)

def main():
    st.set_page_config(
        page_title="Healthcare Gateway Project",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("Healthcare Gateway Project")
    
    # Colonnes pour l'interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Input")
        source_format = st.selectbox(
            "Source Format",
            ["HL7", "FHIR"],
            key="source_format"
        )
        
        # Boutons pour charger les exemples
        if st.button("Load Example Message"):
            if source_format == "HL7":
                message_input = get_hl7_example()
            else:
                message_input = get_fhir_example()
        else:
            message_input = st.session_state.get('message_input', '')
        
        # Zone de texte pour le message
        help_text = "Enter HL7 message in native format" if source_format == "HL7" else "Enter FHIR message in JSON format"
        message_input = st.text_area(
            f"Input Message ({source_format} format)",
            value=message_input,
            height=400,
            help=help_text
        )
        st.session_state['message_input'] = message_input
        
    with col2:
        st.header("Output")
        target_format = st.selectbox(
            "Target Format",
            ["FHIR", "HL7"],
            key="target_format"
        )
        
        if st.button("Transform"):
            try:
                # Préparation du message selon le format source
                if source_format == "HL7":
                    input_data = message_input  # Garder le format texte pour HL7
                else:
                    # Pour FHIR, on vérifie que c'est du JSON valide
                    input_data = json.loads(message_input)
                
                # Préparation de la requête
                payload = {
                    "message": input_data,
                    "source_format": source_format,
                    "target_format": target_format
                }
                
                # Appel API
                response = requests.post(
                    "http://localhost:8000/transform",
                    json=payload
                )
                
                if response.status_code == 200:
                    st.success("Transformation successful!")
                    result = response.json()
                    
                    # Affichage formaté selon le format cible
                    if target_format == "HL7":
                        st.text(result["data"])  # Affichage texte pour HL7
                    else:
                        st.json(result)  # Affichage JSON pour FHIR
                else:
                    st.error(f"Error: {response.text}")
                    
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format (for FHIR): {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
