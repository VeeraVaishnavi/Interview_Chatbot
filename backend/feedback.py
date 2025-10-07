from fastapi import APIRouter # type: ignore
from pydantic import BaseModel
from utils import create_pdf_report
from database import reports_collection  # Firebase Firestore collections

router = APIRouter()

class FeedbackRequest(BaseModel):
    user_id: str
    user_name: str
    job_title: str
    questions_answers: list
    feedback_summary: str

@router.post("/generate_report")
def generate_report(req: FeedbackRequest):
    path = create_pdf_report(req.user_name, req.job_title, req.questions_answers, req.feedback_summary)

    # Firebase version
    doc_ref = reports_collection.document()
    doc_ref.set({
        "user_id": req.user_id,  # just use the string ID
        "report_path": path
    })

    return {"report_path": path}
