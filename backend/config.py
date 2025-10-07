import os
from dotenv import load_dotenv  # type: ignore

# Load .env file
load_dotenv()

# -----------------------------
# API Keys and Environment Config
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# -----------------------------
# Firebase Configuration
# -----------------------------
# Path to your Firebase service account key JSON file
# (Make sure this file exists in your backend folder)
FIREBASE_CREDENTIAL_PATH = os.getenv(
    "FIREBASE_CREDENTIAL_PATH", "serviceAccountKey.json"
)
