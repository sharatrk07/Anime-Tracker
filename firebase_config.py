# firebase_config.py
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

cred_data = st.secrets["firebase"]["firebase_service_account"]
if isinstance(cred_data, str):
    try:
        cred_json = json.loads(cred_data)
    except Exception as e:
        raise Exception("Invalid JSON in secret firebase_service_account") from e
else:
    cred_json = cred_data

cred = credentials.Certificate(cred_json)
firebase_admin.initialize_app(cred)
db = firestore.client()