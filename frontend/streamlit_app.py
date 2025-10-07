import streamlit as st
import requests
import os
import PyPDF2  # type: ignore
from datetime import datetime
from fpdf import FPDF  # type: ignore

st.set_page_config(page_title="AI Interview Chatbot", layout="wide")
BASE_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

# ---------------- helpers ----------------
def signup_user(name, email, password, department=None, year=None):
    payload = {"name": name, "email": email, "password": password}
    if department:
        payload["department"] = department
    if year:
        payload["year"] = year
    try:
        res = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid response from server"}

def login_user(email, password):
    payload = {"email": email, "password": password}
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json=payload)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except ValueError:
        return {"error": "Invalid response from server"}

def schedule_interview(payload):
    res = requests.post(f"{BASE_URL}/interview/schedule_interview", json=payload)
    return res.json()

def generate_question(payload):
    res = requests.post(f"{BASE_URL}/ai/generate_question", json=payload)
    return res.json()

def make_avatar_clip(payload):
    res = requests.post(f"{BASE_URL}/tavus/make_avatar_clip", json=payload)
    return res.json()

def transcribe_upload(file_bytes, filename="audio.webm"):
    files = {"file": (filename, file_bytes)}
    res = requests.post(f"{BASE_URL}/stt/transcribe", files=files)
    return res.json()

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

# ---------------- UI ----------------
page = st.sidebar.selectbox("Navigation", ["Signup", "Login"])

if page == "Signup":
    st.title("Signup")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    department = st.text_input("Department (optional)")
    year = st.text_input("Year (optional)")
    
    if st.button("Signup"):
        res = signup_user(name, email, password, department, year)
        if "error" in res:
            st.error(res["error"])
        else:
            st.success(f"Signup successful! User ID: {res.get('user_id')}")

if page == "Login":
    st.title("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        res = login_user(email, password)
        if "error" in res:
            st.error(res["error"])
        elif "user_id" in res:
            st.success("Login successful")
            st.session_state.user_id = res["user_id"]
            st.session_state.email = res["email"]
            st.session_state.name = res.get("name", "Candidate")

            # ---------------- Schedule Interview ----------------
            st.header("Schedule Interview")
            job_title = st.text_input("Job Title")
            job_desc = st.text_area("Job Description")
            resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            date = st.date_input("Interview Date")
            time_val = st.time_input("Interview Time")

            if st.button("Schedule Interview"):
                resume_text = ""
                if resume_file:
                    resume_text = extract_text_from_pdf(resume_file)

                payload = {
                    "user_id": st.session_state.user_id,
                    "job_title": job_title,
                    "job_description": job_desc,
                    "scheduled_date": str(date),
                    "scheduled_time": str(time_val),
                    "resume_text": resume_text
                }
                r = schedule_interview(payload)
                st.write(r)
                if r.get("meeting_link"):
                    meeting_link = r["meeting_link"]
                    st.success("Interview scheduled and link emailed")
                    st.markdown(f"[Open Meeting]({meeting_link})")
                    st.components.v1.iframe(src=meeting_link, width=1000, height=600)

                    # ---------------- AI Interview ----------------
                    st.header("AI Interview (avatar plays video next to meeting)")
                    questions_answers = []
                    prev_answer = None
                    for i in range(5):
                        q_payload = {
                            "job_title": job_title,
                            "job_desc": job_desc,
                            "resume_text": resume_text,
                            "previous_answer": prev_answer
                        }
                        q_res = generate_question(q_payload)
                        question = q_res.get("question", f"Tell me about yourself (question {i+1})")
                        st.markdown(f"**Q{i+1}:** {question}")

                        tavus_payload = {"avatar_id": "YOUR_AVATAR_ID", "text": question}
                        clip_res = make_avatar_clip(tavus_payload)
                        video_url = clip_res.get("video_url")
                        if video_url:
                            st.video(video_url)

                        # fallback text input for answer
                        answer_text = st.text_input(f"Type your answer for Q{i+1} (or record audio separately):", key=f"ans{i}")
                        questions_answers.append({"question": question, "answer": answer_text})
                        prev_answer = answer_text

                    # ---------------- Feedback & Report ----------------
                    st.header("Feedback & Report")
                    feedback_summary = "Auto-feedback: Focus on clarity, include specific examples, speak confidently."
                    st.write(feedback_summary)

                    if st.button("Generate Report & Download"):
                        payload = {
                            "user_id": st.session_state.user_id,
                            "user_name": st.session_state.name,
                            "job_title": job_title,
                            "questions_answers": questions_answers,
                            "feedback_summary": feedback_summary
                        }
                        rep = requests.post(f"{BASE_URL}/feedback/generate_report", json=payload).json()
                        if rep.get("report_path"):
                            with open(rep["report_path"], "rb") as f:
                                st.download_button("Download PDF Report", f, file_name=os.path.basename(rep["report_path"]))
                        else:
                            st.error("Report generation failed")
