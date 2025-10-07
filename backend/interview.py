from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel
from database import interviews_collection, users_collection
from utils import send_email
import random

router = APIRouter()

class InterviewCreate(BaseModel):
    user_id: str
    job_title: str
    job_description: str = None
    scheduled_date: str
    scheduled_time: str
    resume_text: str = None

@router.post("/schedule_interview")
def schedule_interview(payload: InterviewCreate):
    # Firebase query to get the user
    user_docs = users_collection.document(payload.user_id).get()
    if not user_docs.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user_docs.to_dict()

    # Generate meeting link
    room = f"MockInterview-{random.randint(1000,9999)}"
    meeting_link = f"https://meet.jit.si/{room}"

    # Create interview document
    interview_doc = {
        "user_id": payload.user_id,  # just use the string ID
        "job_title": payload.job_title,
        "job_description": payload.job_description,
        "resume_text": payload.resume_text,
        "scheduled_date": payload.scheduled_date,
        "scheduled_time": payload.scheduled_time,
        "meeting_link": meeting_link,
        "room": room,
    }

    # Firebase insert
    doc_ref = interviews_collection.document()
    doc_ref.set(interview_doc)

    # Send email
    subject = "Your Mock Interview is Scheduled"
    body = f"Hello {user.get('name','Candidate')},\n\nYour mock interview for '{payload.job_title}' is scheduled on {payload.scheduled_date} at {payload.scheduled_time}.\nJoin using this Jitsi link: {meeting_link}\n\nGood luck!"
    send_email(user["email"], subject, body)

    return {"message": "scheduled", "meeting_link": meeting_link, "room": room}
