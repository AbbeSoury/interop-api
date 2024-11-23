Healthcare HL7 to FHIR Gateway
Description
Une gateway de transformation de messages HL7 (Health Level 7) vers FHIR (Fast Healthcare Interoperability Resources) spécialisée dans les messages de rendez-vous (SIU^S12). Cette API REST permet de convertir des messages HL7 en ressources FHIR Appointment tout en préservant les informations essentielles du rendez-vous.
Fonctionnalités
Transformation de messages HL7 SIU^S12 vers FHIR Appointment
Parsing des segments HL7 :
MSH (Message Header)
SCH (Scheduling Information)
PID (Patient Information)
AIG (Agenda Information)
AIL (Location Information)
Gestion des participants :
Patient (ATND)
Agenda (PPRF - Organization)
Créateur (REF - User)
Salle (LOC - Location)
Validation et transformation des dates
Gestion des erreurs robuste
Logs détaillés pour le debugging
Technologies
Python 3.11+
FastAPI
Pydantic
python-hl7
Installation
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

Utilisation
Démarrer le serveur
uvicorn src.api.routes:app --reload

Exemple de requête
curl -X POST "http://localhost:8000/transform" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "MSH|^~\\&|LABO|HOPITAL|SIH|HOPITAL|202403191030||SIU^S12^SIU_S12|...",
           "source_format": "HL7",
           "target_format": "FHIR"
         }'

Format des messages supportés
Message HL7 (Input)
MSH|^~\&|LABO|HOPITAL|SIH|HOPITAL|202403191030||SIU^S12^SIU_S12|20230319103025|P|2.5.1
SCH|12345|28456|||BIOCHEM^Biochemistry^L||||1^once^D|60^minutes|||||||||1234^DUPONT^JEAN^^^^^MD|||||BIOCHEM^Biochemistry Department^L|123 Main St^^Paris^^75001^FRA||||BOOKED
PID|1||IPP123456^^^HOPITAL^PI||DUPONT^JEAN^MARC^^^^L||19800515|M
AIG|1|||Auxiliaires^Auxiliaires
AIL|1||Bureau11^Bureau 11

Ressource FHIR (Output)
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [{
    "resource": {
      "resourceType": "Appointment",
      "status": "booked",
      "serviceType": [{
        "coding": [{
          "code": "BIOCHEM",
          "display": "Biochemistry"
        }]
      }],
      "participant": [
        {
          "actor": {
            "reference": "Patient/IPP123456",
            "display": "DUPONT, JEAN MARC"
          },
          "status": "accepted"
        },
        {
          "actor": {
            "reference": "Organization/Auxiliaires",
            "display": "Auxiliaires"
          },
          "status": "accepted"
        }
      ]
    }
  }]
}

Structure du projet
healthcare-gateway/
├── src/
│   ├── api/
│   │   ├── routes.py      # Endpoints FastAPI
│   │   └── models.py      # Modèles Pydantic
│   ├── gateway/
│   │   ├── core.py        # Logique principale
│   │   └── config.py      # Configuration
│   └── utils/
│       └── parsing.py     # Utilitaires de parsing
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
└── requirements.txt

Tests
# Lancer les tests
pytest tests/

Documentation API
La documentation OpenAPI est disponible à l'adresse :
http://localhost:8000/docs

Contribution
Les contributions sont les bienvenues ! N'hésitez pas à :
Fork le projet
Créer une branche (git checkout -b feature/AmazingFeature)
Commit vos changements (git commit -m 'Add some AmazingFeature')
Push sur la branche (git push origin feature/AmazingFeature)
Ouvrir une Pull Request
Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
Contact
Jules Prugniaud - jules.prugniaud@doctolib.com
Lien du projet : https://github.com/yourusername/healthcare-gateway
