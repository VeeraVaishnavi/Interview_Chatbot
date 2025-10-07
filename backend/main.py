from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore # allow frontend requests
from auth import router as auth_router
from interview import router as interview_router
from ai_questions import router as ai_router
from tavus_integration import router as tavus_router
from stt import router as stt_router
from feedback import router as feedback_router

# -----------------------------
# FastAPI app initialization
# -----------------------------
app = FastAPI(
    title="AI Interview Chatbot Backend",
    description="Backend API for AI-powered interview platform",
    version="1.0.0"
)

# -----------------------------
# CORS Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins; in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Include Routers
# -----------------------------
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(interview_router, prefix="/interview", tags=["Interview"])
app.include_router(ai_router, prefix="/ai", tags=["AI Questions"])
app.include_router(tavus_router, prefix="/tavus", tags=["Avatar/Video"])
app.include_router(stt_router, prefix="/stt", tags=["Speech-to-Text"])
app.include_router(feedback_router, prefix="/feedback", tags=["Feedback/Report"])

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "Welcome to AI Interview Chatbot Backend!"}
