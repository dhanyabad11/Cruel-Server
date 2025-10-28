# SendGrid Setup Guide (FREE - 100 emails/day)

## Why SendGrid?

Digital Ocean blocks SMTP ports (25, 465, 587) by default. SendGrid uses HTTP API instead, bypassing this limitation.

## Setup Steps (5 minutes)

### 1. Create SendGrid Account

1. Go to https://signup.sendgrid.com/
2. Sign up for FREE account (100 emails/day forever)
3. Verify your email address

### 2. Create API Key

1. Login to SendGrid Dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name: `cruel-email-reminders`
5. Permissions: **Full Access** (or at minimum: Mail Send)
6. Click **Create & View**
7. **COPY THE API KEY** (you won't see it again!)

### 3. Verify Sender Email

1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in your details:
    - From Name: `Cruel Deadline Reminders`
    - From Email Address: `dhanyabadbehera@gmail.com` (or any email you own)
    - Reply To: Same email
4. Check your email and verify

### 4. Add to Production

SSH into your droplet and add the environment variable:

```bash
# On your droplet
export SENDGRID_API_KEY="SG.your_api_key_here"
export SENDGRID_FROM_EMAIL="dhanyabadbehera@gmail.com"
```

### 5. Restart Docker Container

The docker run command will include the SendGrid variables.

## Environment Variables Needed

-   `SENDGRID_API_KEY` - Your SendGrid API key (starts with "SG.")
-   `SENDGRID_FROM_EMAIL` - Verified sender email (defaults to SMTP_USERNAME if not set)

## Testing

After setup, the email reminders will automatically use SendGrid instead of SMTP.

## Limits

-   **Free Tier**: 100 emails/day forever
-   **No credit card required**
-   Perfect for student projects!
