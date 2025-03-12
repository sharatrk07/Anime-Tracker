import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if "firebase" not in st.secrets or "firebase_service_account" not in st.secrets["firebase"]:
    raise Exception("Missing firebase_service_account secret in st.secrets.")

cred_str = st.secrets["firebase"]["firebase_service_account"]

if isinstance(cred_str, str):
    try:
        cred_json = json.loads(cred_str)
    except Exception as e:
        raise Exception("Invalid JSON in firebase_service_account secret") from e
else:
    cred_json = cred_str

cred = credentials.Certificate(cred_json)
firebase_admin.initialize_app(cred)
db = firestore.client()
