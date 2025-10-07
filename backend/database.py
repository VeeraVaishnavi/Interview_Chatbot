import firebase_admin # type: ignore
from firebase_admin import credentials, firestore # type: ignore

# Path to your downloaded key
cred = credentials.Certificate("firebase_key.json")

# Initialize Firebase app
firebase_admin.initialize_app(cred)

# Firestore Database
db = firestore.client()

# Collections
users_collection = db.collection("users")
interviews_collection = db.collection("interviews")
qa_collection = db.collection("questions_answers")
reports_collection = db.collection("reports")

print("✅ Connected to Firebase Firestore successfully!")
