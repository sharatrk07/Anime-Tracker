import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

cred = credentials.Certificate(st.secrets["firebase"]["firebase_service_account"])
firebase_admin.initialize_app(cred)
db = firestore.client()