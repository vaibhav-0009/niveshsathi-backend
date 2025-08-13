import firebase_admin
from firebase_admin import credentials, firestore, auth

db = None
auth_client = None

def init_firebase():
    global db, auth_client
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-admin-key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        auth_client = auth
