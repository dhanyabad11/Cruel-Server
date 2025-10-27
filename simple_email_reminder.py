#!/usr/bin/env python3
"""
Simple email reminder - no Redis, no Celery, just works
Run this with: python simple_email_reminder.py
"""
import os
import time
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import httpx

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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def send_email(to_email, subject, body):
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
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code in [200, 202]:
            print(f"✓ Email sent to {to_email}")
            return True
        else:
            print(f"✗ Email failed: {response.status_code} - {response.text}")
            return False

async def check_and_send_reminders():
    """Check deadlines and send email reminders based on user settings"""
    print(f"\n[{datetime.now()}] Checking for deadlines...")
    
    try:
        # Get users with email enabled
        settings = supabase.table('notification_settings').select('*').eq('email_enabled', True).execute()
        
        if not settings.data:
            print("No users with email enabled")
            return
        
        print(f"Found {len(settings.data)} users with email enabled")
        
        for setting in settings.data:
            user_id = setting['user_id']
            
            # Get user email
            user = supabase.table('users').select('email').eq('id', user_id).execute()
            if not user.data:
                continue
            
            email = user.data[0]['email']
            
            # Get pending deadlines for this user
            deadlines = supabase.table('deadlines').select('*').eq('user_id', user_id).execute()
            
            now = datetime.utcnow()
            
            for deadline in deadlines.data:
                deadline_id = deadline['id']
                deadline_date = datetime.fromisoformat(deadline['deadline_date'].replace('Z', '+00:00')).replace(tzinfo=None)
                
                # Get reminder settings for this deadline
                reminders = supabase.table('notification_reminders').select('*').eq('deadline_id', deadline_id).execute()
                
                if not reminders.data:
                    continue
                
                for reminder in reminders.data:
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
                        
                        sent = await send_email(email, subject, body)
                        
                        if sent:
                            # Mark as sent
                            supabase.table('notification_reminders').update({'sent': True}).eq('id', reminder['id']).execute()
                            print(f"Marked reminder {reminder['id']} as sent")
        
        print("Done checking deadlines")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run forever, checking every 5 minutes"""
    print("🚀 Simple Email Reminder Started!")
    print(f"Checking deadlines every 5 minutes...")
    
    while True:
        await check_and_send_reminders()
        print("Sleeping for 5 minutes...")
        await asyncio.sleep(300)  # 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
