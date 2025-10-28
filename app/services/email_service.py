import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

# Initialize Twilio SendGrid client
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", os.getenv("SMTP_USERNAME"))

if not SENDGRID_API_KEY:
    raise ValueError("SENDGRID_API_KEY environment variable is required")

sg = SendGridAPIClient(SENDGRID_API_KEY)

async def send_email(to_email, subject, body):
    """
    Send email using Twilio SendGrid - Simple and reliable!
    Free tier: 100 emails/day
    """
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        response = sg.send(message)
        return True
    except Exception as e:
        raise Exception(f"Twilio SendGrid error: {str(e)}")
