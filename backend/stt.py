# backend/stt.py
from fastapi import APIRouter, File, UploadFile, HTTPException # type: ignore
import requests
from config import OPENAI_API_KEY

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio using OpenAI Whisper API.
    Expects an uploaded audio file (e.g., .mp3, .wav, .m4a, .webm).
    """
    content = await file.read()

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {
        "file": (file.filename, content, file.content_type or "audio/mpeg"),
        "model": (None, "whisper-1")  # OpenAI's Whisper STT model
    }

    response = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers=headers,
        files=files
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"STT error: {response.text}"
        )

    data = response.json()
    transcript = data.get("text")

    return {"transcript": transcript}