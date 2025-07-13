import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "anime-progress-tracker",
    "private_key_id": "77b2636edbbbfa0a0fca1f16f021527f53de8e50",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCmmVEC+Bhm6FnD
... (keep the full key as you provided) ...
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@anime-progress-tracker.iam.gserviceaccount.com",
    "client_id": "108088266466817496846",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40anime-progress-tracker.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'anime-progress-tracker.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()
