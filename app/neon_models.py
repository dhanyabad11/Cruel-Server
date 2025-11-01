"""
SQLAlchemy Database Models for Neon PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Numeric, ForeignKey, JSON
from sqlalchemy.sql import func
from app.neon_database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Deadline(Base):
    __tablename__ = "deadlines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(TIMESTAMP(timezone=True), nullable=False)
    deadline_date = Column(TIMESTAMP(timezone=True))
    priority = Column(String(50), default="medium")
    status = Column(String(50), default="pending")
    portal_id = Column(Integer, ForeignKey("portals.id"))
    portal_task_id = Column(String(255))
    portal_url = Column(String(500))
    tags = Column(Text)
    estimated_hours = Column(Numeric(5, 2))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    email = Column(Text)
    phone_number = Column(Text)
    whatsapp_number = Column(Text)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class NotificationReminder(Base):
    __tablename__ = "notification_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    deadline_id = Column(Integer, ForeignKey("deadlines.id", ondelete="CASCADE"), nullable=False)
    reminder_type = Column(String(50), nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Portal(Base):
    __tablename__ = "portals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    portal_type = Column(String(50), nullable=False)
    url = Column(String(500), nullable=False)
    credentials = Column(JSON)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_sync = Column(TIMESTAMP(timezone=True))
    sync_frequency = Column(String(50), default="daily")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
