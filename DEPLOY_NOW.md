# 🚀 Deploy to Digital Ocean - Real-time Email Reminders

## What This Does:

-   Uses **Twilio SendGrid** (super simple, no complicated setup!)
-   When you create a deadline in your app, it immediately schedules email reminders to the database
-   A background script checks every 5 minutes and sends emails based on your reminder settings (1_hour, 1_day, 1_week, etc.)
-   Real-time: Emails sent automatically as soon as reminder time arrives!

## Setup Steps:

### 1. SSH into your server:

```bash
ssh root@198.211.106.97
cd ai-cruel-backend-updated
```

### 2. Pull latest code:

```bash
git pull
```

### 3. Install Twilio SendGrid library:

```bash
pip3 install sendgrid
```

### 4. Kill old processes:

```bash
pkill -f "python3 simple_email_reminder.py"
pkill -f "uvicorn main:app"
```

### 5. Start email reminder service (checks every 5 minutes):

```bash
nohup python3 simple_email_reminder.py > email_reminders.log 2>&1 &
```

### 6. Start FastAPI backend:

```bash
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

### 7. Check if everything is working:

```bash
# Check if processes are running
ps aux | grep -E "(simple_email|uvicorn)" | grep -v grep

# Check email reminder logs
tail -30 email_reminders.log

# Check backend logs
tail -30 backend.log
```

## How It Works:

1. **Create Deadline in App** → Backend receives request
2. **Backend Schedules Reminders** → Inserts reminder records into `notification_reminders` table
3. **Background Script Checks** → Every 5 minutes, checks if any reminders are due
4. **Sends Email via Twilio SendGrid** → Super simple, no DNS issues, just works!
5. **Marks as Sent** → Updates database so reminder isn't sent again

## Environment Variables Needed:

Make sure `.env` file has:

```
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=dhanyabadbehera@gmail.com
SUPABASE_URL=https://kxlwvqimkhocpgxyjqvb.supabase.co
SUPABASE_ANON_KEY=<your-supabase-key>
```

**(The API keys are already configured on your server in the `.env` file)**

## Test It:

1. Open your app and create a deadline
2. Set reminder for "1 hour before"
3. The script will check every 5 minutes
4. When deadline is within 1 hour, you'll get an email! 📧

## Troubleshooting:

-   **No emails?** Check `email_reminders.log` for errors
-   **Backend not responding?** Check `backend.log`
-   **DNS errors?** Twilio SendGrid uses `requests` library which handles DNS better
-   **Want to test immediately?** Create a deadline due in 6 minutes, set "1_hour" reminder, wait 5 minutes for next check

That's it! Super simple, no Redis, no Celery, no complicated Docker stuff. Just Python + Twilio SendGrid! 🎉
