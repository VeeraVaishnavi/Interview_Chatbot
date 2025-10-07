from fastapi import APIRouter # type: ignore
from pydantic import BaseModel
import openai # type: ignore
from config import OPENAI_API_KEY

router = APIRouter()
openai.api_key = OPENAI_API_KEY

class QRequest(BaseModel):
    job_title: str
    job_desc: str
    resume_text: str
    previous_answer: str = None

@router.post("/generate_question")
def generate_question(req: QRequest):
    prompt = f"""
You are an experienced interviewer for the position: {req.job_title}.
Job description: {req.job_desc}
Candidate resume snippets: {req.resume_text}
Last candidate answer: {req.previous_answer}

Generate ONE concise interview question that is appropriate as the next question.
Return only the question text.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":"You are a professional interviewer."},
                  {"role":"user","content":prompt}],
        max_tokens=120,
        temperature=0.7
    )
    q = resp["choices"][0]["message"]["content"].strip()
    return {"question": q}
