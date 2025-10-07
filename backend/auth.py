from fastapi import APIRouter, HTTPException # type: ignore
from passlib.context import CryptContext # type: ignore
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import users_collection  # ✅ correct
  # type: ignore # ✅ from our Firebase setup

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# Pydantic Models
# -----------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: Optional[str] = None
    year: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# -----------------------------
# Signup Endpoint
# -----------------------------
@router.post("/signup")
def signup(user: UserCreate):
    # Check if user already exists
    existing_user = users_collection.where("email", "==", user.email).stream()
    if any(existing_user):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed = pwd_context.hash(user.password)

    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed,
        "department": user.department,
        "year": user.year
    }

    doc_ref = users_collection.document()
    doc_ref.set(user_data)

    return {"message": "Signup successful", "user_id": doc_ref.id}

# -----------------------------
# Login Endpoint
# -----------------------------
@router.post("/login")
def login(user: UserLogin):
    user_docs = users_collection.where("email", "==", user.email).stream()
    db_user = None
    for doc in user_docs:
        db_user = doc.to_dict()
        db_user["id"] = doc.id
        break

    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user["id"],
        "email": db_user["email"],
        "name": db_user.get("name")
    }
