"""skills/email_ops.py"""
import smtplib, os, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

class EmailOps:
    def __init__(self):
        self._sender = os.getenv("EMAIL_ADDRESS","")
        self._pwd = os.getenv("EMAIL_PASSWORD","")

    def send_email(self, q) -> str:
        if not self._sender or not self._pwd:
            return "Email not configured. Add EMAIL_ADDRESS and EMAIL_PASSWORD to .env"
        to = re.search(r'to\s+([\w\.\-]+@[\w\.\-]+)', q, re.I)
        if not to: return "Please specify recipient email."
        subj = re.search(r'(?:subject|about)\s+["\']?(.+?)["\']?(?:\s+saying|$)', q, re.I)
        body = re.search(r'(?:saying|body|message)\s+["\']?(.+)["\']?', q, re.I)
        msg = MIMEMultipart()
        msg["From"] = self._sender
        msg["To"] = to.group(1)
        msg["Subject"] = subj.group(1) if subj else "Message from NEXUS"
        msg.attach(MIMEText(body.group(1) if body else "Sent via NEXUS.", "plain"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(self._sender, self._pwd)
                s.sendmail(self._sender, to.group(1), msg.as_string())
            return f"Email sent to {to.group(1)}."
        except Exception as e: return f"Email failed: {e}"
