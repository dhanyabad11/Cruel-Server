-- ===================================
-- NEON DATABASE SCHEMA (No Authentication)
-- Run this in your Neon SQL Editor
-- ===================================

-- 1. Create users table (simplified, no auth)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create deadlines table
CREATE TABLE IF NOT EXISTS deadlines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMPTZ NOT NULL,
    deadline_date TIMESTAMPTZ,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',
    portal_id INTEGER,
    portal_task_id VARCHAR(255),
    portal_url VARCHAR(500),
    tags TEXT,
    estimated_hours NUMERIC(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Create notification_settings table
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    email TEXT,
    phone_number TEXT,
    whatsapp_number TEXT,
    email_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT false,
    whatsapp_enabled BOOLEAN DEFAULT false,
    push_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Create notification_reminders table
CREATE TABLE IF NOT EXISTS notification_reminders (
    id SERIAL PRIMARY KEY,
    deadline_id INTEGER NOT NULL,
    reminder_type VARCHAR(50) NOT NULL,
    sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (deadline_id) REFERENCES deadlines(id) ON DELETE CASCADE
);

-- 5. Create portals table
CREATE TABLE IF NOT EXISTS portals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    portal_type VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    credentials JSONB,
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMPTZ,
    sync_frequency VARCHAR(50) DEFAULT 'daily',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Create indexes
CREATE INDEX idx_deadlines_user_id ON deadlines(user_id);
CREATE INDEX idx_deadlines_due_date ON deadlines(due_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_notification_settings_user_id ON notification_settings(user_id);
CREATE INDEX idx_notification_reminders_deadline_id ON notification_reminders(deadline_id);
CREATE INDEX idx_notification_reminders_sent ON notification_reminders(sent);
CREATE INDEX idx_portals_user_id ON portals(user_id);

-- 7. Create a default user for testing
INSERT INTO users (email, name) 
VALUES ('test@example.com', 'Test User')
ON CONFLICT (email) DO NOTHING;

-- ===================================
-- ✅ NEON DATABASE READY (No Auth Required)
-- Next: Update your backend to use Neon connection string
-- ===================================
