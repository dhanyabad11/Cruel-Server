#!/usr/bin/env python3
"""
Simple email reminder using Twilio SendGrid + Neon PostgreSQL
Run this with: python simple_email_reminder.py
"""
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Twilio SendGrid config
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "dhanyabadbehera@gmail.com")

# Neon PostgreSQL config
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate config
if not DATABASE_URL:
    print(f"ERROR: Missing DATABASE_URL!")
    exit(1)

if not SENDGRID_API_KEY:
    print(f"ERROR: Missing SendGrid API key!")
    exit(1)

print(f"✓ Config loaded - Database: {DATABASE_URL[:50]}...")
print(f"✓ Twilio SendGrid from: {SENDGRID_FROM_EMAIL}")

# Create database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Initialize Twilio SendGrid client
sg = SendGridAPIClient(SENDGRID_API_KEY)

def send_email(to_email, subject, body):
    """Send email via Twilio SendGrid - super simple!"""
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        response = sg.send(message)
        print(f"✓ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

def check_and_send_reminders():
    """Check deadlines and send email reminders based on user settings"""
    print(f"\n[{datetime.now()}] Checking for deadlines...")
    
    db = SessionLocal()
    try:
        # Get users with email enabled
        query = text("""
            SELECT DISTINCT ns.user_id, u.email
            FROM notification_settings ns
            JOIN users u ON u.id = ns.user_id
            WHERE ns.email_enabled = true
        """)
        
        settings = db.execute(query).fetchall()
        
        if not settings:
            print("No users with email enabled")
            return
        
        print(f"Found {len(settings)} users with email enabled")
        
        for user_id, email in settings:
            # Get pending deadlines for this user
            deadlines_query = text("""
                SELECT id, title, description, due_date
                FROM deadlines
                WHERE user_id = :user_id
            """)
            deadlines = db.execute(deadlines_query, {"user_id": user_id}).fetchall()
            
            now = datetime.utcnow()
            
            for deadline_id, title, description, due_date in deadlines:
                # Get reminder settings for this deadline
                reminders_query = text("""
                    SELECT id, reminder_type, sent
                    FROM notification_reminders
                    WHERE deadline_id = :deadline_id
                """)
                reminders = db.execute(reminders_query, {"deadline_id": deadline_id}).fetchall()
                
                if not reminders:
                    continue
                
                for reminder_id, reminder_type, sent in reminders:
                    # Skip if already sent
                    if sent:
                        continue
                    
                    # Calculate when to send based on reminder type
                    time_map = {
                        '1_hour': timedelta(hours=1),
                        '1_day': timedelta(days=1),
                        '1_week': timedelta(weeks=1),
                        '2_weeks': timedelta(weeks=2),
                        '1_month': timedelta(days=30)
                    }
                    
                    time_before = time_map.get(reminder_type)
                    if not time_before:
                        continue
                    
                    time_until = due_date - now
                    
                    # Send if within 5 minutes of the reminder time
                    if abs(time_until - time_before) <= timedelta(minutes=5):
                        subject = f"⏰ Deadline Reminder: {title}"
                        body = f"Hi!\n\nReminder: Your deadline '{title}' is coming up on {due_date}.\n\nDescription: {description or 'N/A'}\n\nTime remaining: {reminder_type.replace('_', ' ')}\n\nStay on track!"
                        
                        email_sent = send_email(email, subject, body)
                        
                        if email_sent:
                            # Mark as sent
                            update_query = text("""
                                UPDATE notification_reminders
                                SET sent = true, sent_at = NOW()
                                WHERE id = :reminder_id
                            """)
                            db.execute(update_query, {"reminder_id": reminder_id})
                            db.commit()
                            print(f"Marked reminder {reminder_id} as sent")
        
        print("Done checking deadlines")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    """Run forever, checking every 5 minutes"""
    print("🚀 Simple Email Reminder Started!")
    print(f"Checking deadlines every 5 minutes...")
    
    while True:
        check_and_send_reminders()
        print("Sleeping for 5 minutes...")
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
