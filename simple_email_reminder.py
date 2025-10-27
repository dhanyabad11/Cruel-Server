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
    """Check deadlines and send email reminders"""
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
            
            # Get deadlines for this user
            deadlines = supabase.table('deadlines').select('*').eq('user_id', user_id).execute()
            
            now = datetime.utcnow()
            
            for deadline in deadlines.data:
                deadline_date = datetime.fromisoformat(deadline['deadline_date'].replace('Z', '+00:00')).replace(tzinfo=None)
                time_until = deadline_date - now
                
                # Check if we should send 1 day reminder
                if timedelta(hours=23, minutes=55) <= time_until <= timedelta(hours=24, minutes=5):
                    subject = f"⏰ Deadline Tomorrow: {deadline['title']}"
                    body = f"Hi!\n\nYour deadline '{deadline['title']}' is tomorrow at {deadline_date}.\n\nDescription: {deadline.get('description', 'N/A')}\n\nDon't forget!"
                    await send_email(email, subject, body)
                
                # Check if we should send 1 hour reminder
                elif timedelta(minutes=55) <= time_until <= timedelta(hours=1, minutes=5):
                    subject = f"🚨 Deadline in 1 Hour: {deadline['title']}"
                    body = f"Hi!\n\nYour deadline '{deadline['title']}' is in 1 HOUR at {deadline_date}.\n\nDescription: {deadline.get('description', 'N/A')}\n\nHurry!"
                    await send_email(email, subject, body)
        
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
