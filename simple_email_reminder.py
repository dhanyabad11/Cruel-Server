#!/usr/bin/env python3
"""
Simple email reminder - no Redis, no Celery, just works
Run this with: python simple_email_reminder.py
"""
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import json

load_dotenv()

# SendGrid config
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "dhanyabadbehera@gmail.com")

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Validate config
if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"ERROR: Missing Supabase config!")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'SET' if SUPABASE_KEY else 'MISSING'}")
    exit(1)

if not SENDGRID_API_KEY:
    print(f"ERROR: Missing SendGrid API key!")
    exit(1)

print(f"✓ Config loaded - Supabase: {SUPABASE_URL[:30]}...")
print(f"✓ SendGrid from: {SENDGRID_FROM_EMAIL}")

# Supabase headers for REST API
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def send_email(to_email, subject, body):
    """Send email via SendGrid"""
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": SENDGRID_FROM_EMAIL},
        "content": [{"type": "text/plain", "value": body}]
    }
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 202]:
        print(f"✓ Email sent to {to_email}")
        return True
    else:
        print(f"✗ Email failed: {response.status_code} - {response.text}")
        return False

def check_and_send_reminders():
    """Check deadlines and send email reminders based on user settings"""
    print(f"\n[{datetime.now()}] Checking for deadlines...")
    
    try:
        # Get users with email enabled using REST API
        settings_url = f"{SUPABASE_URL}/rest/v1/notification_settings?email_enabled=eq.true&select=*"
        settings_response = requests.get(settings_url, headers=SUPABASE_HEADERS)
        settings = settings_response.json()
        
        if not settings:
            print("No users with email enabled")
            return
        
        print(f"Found {len(settings)} users with email enabled")
        
        for setting in settings:
            user_id = setting['user_id']
            
            # Get user email using REST API
            user_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=email"
            user_response = requests.get(user_url, headers=SUPABASE_HEADERS)
            user_data = user_response.json()
            
            if not user_data:
                continue
            
            email = user_data[0]['email']
            
            # Get pending deadlines for this user
            deadlines_url = f"{SUPABASE_URL}/rest/v1/deadlines?user_id=eq.{user_id}&select=*"
            deadlines_response = requests.get(deadlines_url, headers=SUPABASE_HEADERS)
            deadlines = deadlines_response.json()
            
            now = datetime.utcnow()
            
            for deadline in deadlines:
                deadline_id = deadline['id']
                deadline_date = datetime.fromisoformat(deadline['deadline_date'].replace('Z', '+00:00')).replace(tzinfo=None)
                
                # Get reminder settings for this deadline
                reminders_url = f"{SUPABASE_URL}/rest/v1/notification_reminders?deadline_id=eq.{deadline_id}&select=*"
                reminders_response = requests.get(reminders_url, headers=SUPABASE_HEADERS)
                reminders = reminders_response.json()
                
                if not reminders:
                    continue
                
                for reminder in reminders:
                    # Skip if already sent
                    if reminder.get('sent'):
                        continue
                    
                    reminder_type = reminder['reminder_type']  # 1_hour, 1_day, 1_week, etc.
                    
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
                    
                    time_until = deadline_date - now
                    
                    # Send if within 5 minutes of the reminder time
                    if abs(time_until - time_before) <= timedelta(minutes=5):
                        subject = f"⏰ Deadline Reminder: {deadline['title']}"
                        body = f"Hi!\n\nReminder: Your deadline '{deadline['title']}' is coming up on {deadline_date}.\n\nDescription: {deadline.get('description', 'N/A')}\n\nTime remaining: {reminder_type.replace('_', ' ')}\n\nStay on track!"
                        
                        sent = send_email(email, subject, body)
                        
                        if sent:
                            # Mark as sent using REST API
                            update_url = f"{SUPABASE_URL}/rest/v1/notification_reminders?id=eq.{reminder['id']}"
                            update_data = {"sent": True}
                            requests.patch(update_url, json=update_data, headers=SUPABASE_HEADERS)
                            print(f"Marked reminder {reminder['id']} as sent")
        
        print("Done checking deadlines")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

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
