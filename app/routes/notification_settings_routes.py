"""
Notification Settings Routes using Neon PostgreSQL (No Authentication)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.neon_database import get_db
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["notification-settings"])

# Default user ID (since no auth)
DEFAULT_USER_ID = 1

@router.get("/notifications")
async def get_notification_settings(db: Session = Depends(get_db)):
    """Get user's notification settings with all reminder configurations"""
    try:
        # Get existing settings
        settings_query = text("""
            SELECT id, user_id, email, phone_number, whatsapp_number,
                   email_enabled, sms_enabled, whatsapp_enabled, push_enabled,
                   created_at, updated_at
            FROM notification_settings
            WHERE user_id = :user_id
        """)
        
        result = db.execute(settings_query, {"user_id": DEFAULT_USER_ID}).first()
        
        if not result:
            # Get user email
            user_query = text("SELECT email FROM users WHERE id = :user_id")
            user_result = db.execute(user_query, {"user_id": DEFAULT_USER_ID}).first()
            user_email = user_result[0] if user_result else "user@example.com"
            
            # Create default settings
            insert_query = text("""
                INSERT INTO notification_settings 
                (user_id, email, phone_number, whatsapp_number, email_enabled, 
                 sms_enabled, whatsapp_enabled, push_enabled)
                VALUES (:user_id, :email, NULL, NULL, true, false, false, true)
                RETURNING id, user_id, email, phone_number, whatsapp_number,
                          email_enabled, sms_enabled, whatsapp_enabled, push_enabled,
                          created_at, updated_at
            """)
            
            result = db.execute(insert_query, {
                "user_id": DEFAULT_USER_ID,
                "email": user_email
            })
            db.commit()
            result = result.first()
        
        settings = {
            "id": result[0],
            "user_id": result[1],
            "email": result[2],
            "phone_number": result[3],
            "whatsapp_number": result[4],
            "email_enabled": result[5],
            "sms_enabled": result[6],
            "whatsapp_enabled": result[7],
            "push_enabled": result[8],
            "created_at": result[9].isoformat() if result[9] else None,
            "updated_at": result[10].isoformat() if result[10] else None,
        }
        
        # Get all reminder configurations
        reminders_query = text("""
            SELECT id, user_id, reminder_time, email_enabled, sms_enabled,
                   whatsapp_enabled, push_enabled, created_at, updated_at
            FROM notification_reminders
            WHERE user_id = :user_id
            ORDER BY reminder_time
        """)
        
        reminder_results = db.execute(reminders_query, {"user_id": DEFAULT_USER_ID})
        reminders = []
        
        for row in reminder_results:
            reminders.append({
                "id": row[0],
                "user_id": row[1],
                "reminder_time": row[2],
                "email_enabled": row[3],
                "sms_enabled": row[4],
                "whatsapp_enabled": row[5],
                "push_enabled": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
            })
        
        # Create default reminder if none exist
        if not reminders:
            default_query = text("""
                INSERT INTO notification_reminders
                (user_id, reminder_time, email_enabled, sms_enabled, whatsapp_enabled, push_enabled)
                VALUES (:user_id, '1_day', true, false, false, true)
                RETURNING id, user_id, reminder_time, email_enabled, sms_enabled,
                          whatsapp_enabled, push_enabled, created_at, updated_at
            """)
            
            result = db.execute(default_query, {"user_id": DEFAULT_USER_ID})
            db.commit()
            row = result.first()
            
            reminders = [{
                "id": row[0],
                "user_id": row[1],
                "reminder_time": row[2],
                "email_enabled": row[3],
                "sms_enabled": row[4],
                "whatsapp_enabled": row[5],
                "push_enabled": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
            }]
        
        return {
            "settings": settings,
            "reminders": reminders
        }
        
    except Exception as e:
        print(f"ERROR: Failed to get notification settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

@router.put("/notifications")
async def update_notification_settings(
    settings_data: dict,
    db: Session = Depends(get_db)
):
    """Update notification settings"""
    try:
        # Build update query
        update_fields = []
        params = {"user_id": DEFAULT_USER_ID}
        
        if "email" in settings_data:
            update_fields.append("email = :email")
            params["email"] = settings_data["email"]
        if "phone_number" in settings_data:
            update_fields.append("phone_number = :phone_number")
            params["phone_number"] = settings_data["phone_number"]
        if "whatsapp_number" in settings_data:
            update_fields.append("whatsapp_number = :whatsapp_number")
            params["whatsapp_number"] = settings_data["whatsapp_number"]
        if "email_enabled" in settings_data:
            update_fields.append("email_enabled = :email_enabled")
            params["email_enabled"] = settings_data["email_enabled"]
        if "sms_enabled" in settings_data:
            update_fields.append("sms_enabled = :sms_enabled")
            params["sms_enabled"] = settings_data["sms_enabled"]
        if "whatsapp_enabled" in settings_data:
            update_fields.append("whatsapp_enabled = :whatsapp_enabled")
            params["whatsapp_enabled"] = settings_data["whatsapp_enabled"]
        if "push_enabled" in settings_data:
            update_fields.append("push_enabled = :push_enabled")
            params["push_enabled"] = settings_data["push_enabled"]
        
        update_fields.append("updated_at = NOW()")
        
        query = text(f"""
            UPDATE notification_settings
            SET {', '.join(update_fields)}
            WHERE user_id = :user_id
            RETURNING id, user_id, email, phone_number, whatsapp_number,
                      email_enabled, sms_enabled, whatsapp_enabled, push_enabled,
                      created_at, updated_at
        """)
        
        result = db.execute(query, params)
        db.commit()
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        return {
            "id": row[0],
            "user_id": row[1],
            "email": row[2],
            "phone_number": row[3],
            "whatsapp_number": row[4],
            "email_enabled": row[5],
            "sms_enabled": row[6],
            "whatsapp_enabled": row[7],
            "push_enabled": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to update notification settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.post("/reminders")
async def create_notification_reminder(
    reminder_data: dict,
    db: Session = Depends(get_db)
):
    """Create or update a notification reminder configuration"""
    try:
        # Check if reminder exists for this reminder_time
        check_query = text("""
            SELECT id FROM notification_reminders
            WHERE user_id = :user_id AND reminder_time = :reminder_time
        """)
        
        exists = db.execute(check_query, {
            "user_id": DEFAULT_USER_ID,
            "reminder_time": reminder_data.get("reminder_time")
        }).first()
        
        if exists:
            # Update existing
            query = text("""
                UPDATE notification_reminders
                SET email_enabled = :email_enabled,
                    sms_enabled = :sms_enabled,
                    whatsapp_enabled = :whatsapp_enabled,
                    push_enabled = :push_enabled,
                    updated_at = NOW()
                WHERE user_id = :user_id AND reminder_time = :reminder_time
                RETURNING id, user_id, reminder_time, email_enabled, sms_enabled,
                          whatsapp_enabled, push_enabled, created_at, updated_at
            """)
        else:
            # Insert new
            query = text("""
                INSERT INTO notification_reminders
                (user_id, reminder_time, email_enabled, sms_enabled, whatsapp_enabled, push_enabled)
                VALUES (:user_id, :reminder_time, :email_enabled, :sms_enabled, :whatsapp_enabled, :push_enabled)
                RETURNING id, user_id, reminder_time, email_enabled, sms_enabled,
                          whatsapp_enabled, push_enabled, created_at, updated_at
            """)
        
        result = db.execute(query, {
            "user_id": DEFAULT_USER_ID,
            "reminder_time": reminder_data.get("reminder_time"),
            "email_enabled": reminder_data.get("email_enabled", True),
            "sms_enabled": reminder_data.get("sms_enabled", False),
            "whatsapp_enabled": reminder_data.get("whatsapp_enabled", False),
            "push_enabled": reminder_data.get("push_enabled", True),
        })
        db.commit()
        row = result.first()
        
        return {
            "id": row[0],
            "user_id": row[1],
            "reminder_time": row[2],
            "email_enabled": row[3],
            "sms_enabled": row[4],
            "whatsapp_enabled": row[5],
            "push_enabled": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "updated_at": row[8].isoformat() if row[8] else None,
        }
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create/update reminder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create reminder: {str(e)}")

@router.delete("/reminders/{reminder_time}")
async def delete_notification_reminder(
    reminder_time: str,
    db: Session = Depends(get_db)
):
    """Delete a specific reminder configuration"""
    try:
        query = text("""
            DELETE FROM notification_reminders
            WHERE user_id = :user_id AND reminder_time = :reminder_time
            RETURNING id
        """)
        
        result = db.execute(query, {
            "user_id": DEFAULT_USER_ID,
            "reminder_time": reminder_time
        })
        db.commit()
        
        if not result.first():
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {"message": f"Reminder for {reminder_time} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to delete reminder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete reminder: {str(e)}")
