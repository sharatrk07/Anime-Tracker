# firebase_config.py
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

cert_str = st.secrets["firebase"]["firebase_service_account"].strip()
cred = credentials.Certificate(json.loads(cert_str))
firebase_admin.initialize_app(cred)
db = firestore.client()
