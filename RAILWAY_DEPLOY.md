# 🚂 Deploy to Railway - No DNS Issues!

Railway is much simpler than Digital Ocean and doesn't have DNS problems. Your Twilio SendGrid + Supabase will work perfectly!

## Quick Deploy (5 minutes):

### 1. Create Railway Account

-   Go to https://railway.app
-   Sign up with GitHub (free $5/month credit)

### 2. Deploy Backend

Click this button or follow steps:

**Option A: One-Click Deploy**

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose `dhanyabad11/Cruel-Server`
4. Railway will auto-detect it's a Python app!

**Option B: Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
cd /Users/dhanyabad/code2/cruel/ai-cruel/backend
railway init

# Deploy
railway up
```

### 3. Add Environment Variables

In Railway Dashboard → Your Project → Variables:

```
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=dhanyabadbehera@gmail.com
SUPABASE_URL=https://kxlwvqimkhocpgxyjqvb.supabase.co
SUPABASE_ANON_KEY=<your-supabase-anon-key>
PORT=8000
```

### 4. Configure Start Command

Railway → Settings → Deploy:

-   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Deploy Email Reminder Service

Create a **second Railway service** for the reminder script:

1. Same repo, different start command
2. Start Command: `python3 simple_email_reminder.py`
3. Same environment variables

### 6. Get Your Backend URL

Railway will give you a URL like:
`https://your-app.railway.app`

Update your frontend to use this URL!

## Why Railway?

✅ **No DNS issues** - Everything just works  
✅ **Free $5/month** - Enough for your app  
✅ **Auto-scaling** - Handles traffic spikes  
✅ **GitHub integration** - Auto-deploys on push  
✅ **Simple setup** - No SSH, no server management  
✅ **Logs built-in** - See errors in real-time

## Alternative: Render.com

If you prefer Render:

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Add environment variables
5. Deploy!

Both Railway and Render are 10x easier than Digital Ocean for this use case!

## Next Steps:

1. Deploy backend to Railway
2. Deploy reminder service to Railway (separate service)
3. Update frontend API URL
4. Test creating a deadline
5. Check Railway logs to see emails being sent!

No more DNS headaches! 🎉
