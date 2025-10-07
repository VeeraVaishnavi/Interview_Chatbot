from pydantic import BaseModel, EmailStr
from typing import Optional

# -----------------------------
# User Schemas
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
# Interview Schema
# -----------------------------
class InterviewCreate(BaseModel):
    user_id: str  # just a string ID in Firebase
    job_title: str
    job_description: Optional[str] = None
    scheduled_date: str
    scheduled_time: str
