import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2 # type: ignore
from fpdf import FPDF # type: ignore
import os
from datetime import datetime
from config import SMTP_EMAIL, SMTP_PASSWORD

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

def extract_text_from_pdf_bytes(file_bytes):
    # file_bytes: bytes-like object (e.g., file.read())
    reader = PyPDF2.PdfReader(file_bytes)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

def create_pdf_report(user_name, job_title, questions_answers, feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Mock Interview Report - {user_name}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Job Title: {job_title}", ln=True)
    pdf.ln(5)

    for i, qa in enumerate(questions_answers, 1):
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 7, f"Q{i}: {qa.get('question')}")
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 7, f"A{i}: {qa.get('answer')}")
        pdf.ln(2)

    pdf.ln(6)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "Feedback", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 7, feedback)

    filename = f"report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("generated_reports", exist_ok=True)
    path = os.path.join("generated_reports", filename)
    pdf.output(path)
    return path
