from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel
import requests
from config import TAVUS_API_KEY
from database import qa_collection  # Firebase Firestore collection

router = APIRouter()

class TavusRequest(BaseModel):
    avatar_id: str
    text: str

# 1. Start video generation
@router.post("/make_avatar_clip")
def make_avatar_clip(req: TavusRequest):
    if not TAVUS_API_KEY:
        raise HTTPException(status_code=500, detail="TAVUS_API_KEY not configured")

    tavus_url = "https://api.tavus.io/v1/videos"
    headers = {
        "Authorization": f"Bearer {TAVUS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "persona_id": req.avatar_id,
        "script": req.text
    }

    r = requests.post(tavus_url, json=payload, headers=headers)
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Tavus error: {r.text}")

    data = r.json()
    video_id = data.get("id")
    if not video_id:
        raise HTTPException(status_code=500, detail="No video ID returned by Tavus")

    # Save job info in Firebase
    doc_ref = qa_collection.document(video_id)
    doc_ref.set({
        "avatar_id": req.avatar_id,
        "text": req.text,
        "video_id": video_id,
        "status": "processing"
    })

    return {"video_id": video_id, "status": "processing"}

# 2. Poll later to check video status
@router.get("/check_avatar_clip/{video_id}")
def check_avatar_clip(video_id: str):
    if not TAVUS_API_KEY:
        raise HTTPException(status_code=500, detail="TAVUS_API_KEY not configured")

    url = f"https://api.tavus.io/v1/videos{video_id}"
    headers = {"Authorization": f"Bearer {TAVUS_API_KEY}"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Tavus error: {r.text}")

    data = r.json()
    status = data.get("status")
    video_url = data.get("video_url")

    # Update DB in Firebase
    doc_ref = qa_collection.document(video_id)
    doc_ref.update({
        "status": status,
        "video_url": video_url
    })

    return {"video_id": video_id, "status": status, "video_url": video_url}
