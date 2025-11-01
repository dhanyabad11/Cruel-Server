"""
Deadline Routes using Neon PostgreSQL (No Authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from app.neon_database import get_db
from app.services.email_service import send_email

router = APIRouter(tags=["deadlines"])

# Default user ID (since no auth)
DEFAULT_USER_ID = 1

async def schedule_email_reminders(deadline_id: int, user_email: str, db: Session):
    """Schedule email reminders based on user settings"""
    try:
        # Create default reminder records in database
        reminder_types = ['1_hour', '1_day']  # Default reminders
        
        for reminder_type in reminder_types:
            query = text("""
                INSERT INTO notification_reminders (deadline_id, reminder_type, sent)
                VALUES (:deadline_id, :reminder_type, false)
            """)
            db.execute(query, {
                "deadline_id": deadline_id,
                "reminder_type": reminder_type
            })
        
        db.commit()
        print(f"✓ Scheduled {len(reminder_types)} email reminders for deadline {deadline_id}")
    except Exception as e:
        print(f"✗ Failed to schedule reminders: {e}")
        db.rollback()

@router.get("/")
async def get_deadlines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all deadlines for the default user"""
    try:
        query = """
            SELECT id, title, description, due_date, priority, status, 
                   created_at, updated_at, deadline_date
            FROM deadlines
            WHERE user_id = :user_id
        """
        
        params = {"user_id": DEFAULT_USER_ID}
        
        if status:
            query += " AND status = :status"
            params["status"] = status
            
        if priority:
            query += " AND priority = :priority"
            params["priority"] = priority
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip
        
        result = db.execute(text(query), params)
        deadlines = []
        
        for row in result:
            deadlines.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "due_date": row[3].isoformat() if row[3] else None,
                "priority": row[4],
                "status": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None,
                "deadline_date": row[8].isoformat() if row[8] else None,
            })
        
        print(f"DEBUG: Retrieved {len(deadlines)} deadlines from database")
        return deadlines
        
    except Exception as e:
        print(f"ERROR: Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/")
async def create_deadline(
    deadline_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new deadline in Neon database"""
    try:
        print(f"DEBUG: Creating deadline")
        print(f"DEBUG: Raw deadline data: {deadline_data}")
        
        # Get user email for reminders
        user_query = text("SELECT email FROM users WHERE id = :user_id")
        user_result = db.execute(user_query, {"user_id": DEFAULT_USER_ID}).first()
        user_email = user_result[0] if user_result else None
        
        # Insert into database
        insert_query = text("""
            INSERT INTO deadlines (user_id, title, description, due_date, priority, status)
            VALUES (:user_id, :title, :description, :due_date, :priority, :status)
            RETURNING id, title, description, due_date, priority, status, created_at
        """)
        
        result = db.execute(insert_query, {
            "user_id": DEFAULT_USER_ID,
            "title": deadline_data.get("title", ""),
            "description": deadline_data.get("description", ""),
            "due_date": deadline_data.get("due_date", ""),
            "priority": deadline_data.get("priority", "medium"),
            "status": "pending"
        })
        
        db.commit()
        
        row = result.first()
        created_deadline = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "due_date": row[3].isoformat() if row[3] else None,
            "priority": row[4],
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        }
        
        print(f"DEBUG: Successfully created deadline: {created_deadline}")
        
        # Schedule email reminders in background
        if user_email:
            background_tasks.add_task(
                schedule_email_reminders,
                created_deadline['id'],
                user_email,
                db
            )
        
        return created_deadline
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create deadline: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create deadline: {str(e)}")

@router.get("/{deadline_id}")
async def get_deadline(
    deadline_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific deadline by ID"""
    query = text("""
        SELECT id, title, description, due_date, priority, status, created_at, updated_at
        FROM deadlines
        WHERE id = :deadline_id AND user_id = :user_id
    """)
    
    result = db.execute(query, {
        "deadline_id": deadline_id,
        "user_id": DEFAULT_USER_ID
    }).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Deadline not found")
    
    return {
        "id": result[0],
        "title": result[1],
        "description": result[2],
        "due_date": result[3].isoformat() if result[3] else None,
        "priority": result[4],
        "status": result[5],
        "created_at": result[6].isoformat() if result[6] else None,
        "updated_at": result[7].isoformat() if result[7] else None,
    }

@router.put("/{deadline_id}")
async def update_deadline(
    deadline_id: int,
    deadline_data: dict,
    db: Session = Depends(get_db)
):
    """Update a deadline in Neon"""
    try:
        # Build update query dynamically
        update_fields = []
        params = {"deadline_id": deadline_id, "user_id": DEFAULT_USER_ID}
        
        if "title" in deadline_data:
            update_fields.append("title = :title")
            params["title"] = deadline_data["title"]
        if "description" in deadline_data:
            update_fields.append("description = :description")
            params["description"] = deadline_data["description"]
        if "due_date" in deadline_data:
            update_fields.append("due_date = :due_date")
            params["due_date"] = deadline_data["due_date"]
        if "priority" in deadline_data:
            update_fields.append("priority = :priority")
            params["priority"] = deadline_data["priority"]
        if "status" in deadline_data:
            update_fields.append("status = :status")
            params["status"] = deadline_data["status"]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = NOW()")
        
        query = text(f"""
            UPDATE deadlines
            SET {', '.join(update_fields)}
            WHERE id = :deadline_id AND user_id = :user_id
            RETURNING id, title, description, due_date, priority, status, created_at, updated_at
        """)
        
        result = db.execute(query, params)
        db.commit()
        
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Deadline not found")
        
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "due_date": row[3].isoformat() if row[3] else None,
            "priority": row[4],
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to update deadline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update deadline: {str(e)}")

@router.delete("/{deadline_id}")
async def delete_deadline(
    deadline_id: int,
    db: Session = Depends(get_db)
):
    """Delete a deadline from Neon"""
    try:
        query = text("""
            DELETE FROM deadlines
            WHERE id = :deadline_id AND user_id = :user_id
            RETURNING id
        """)
        
        result = db.execute(query, {
            "deadline_id": deadline_id,
            "user_id": DEFAULT_USER_ID
        })
        db.commit()
        
        if not result.first():
            raise HTTPException(status_code=404, detail="Deadline not found")
        
        return {"message": "Deadline deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to delete deadline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete deadline: {str(e)}")

@router.get("/stats/overview")
async def get_deadline_stats(db: Session = Depends(get_db)):
    """Get deadline statistics"""
    query = text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'overdue' THEN 1 END) as overdue
        FROM deadlines
        WHERE user_id = :user_id
    """)
    
    result = db.execute(query, {"user_id": DEFAULT_USER_ID}).first()
    
    return {
        "total": result[0] or 0,
        "pending": result[1] or 0,
        "in_progress": result[2] or 0,
        "completed": result[3] or 0,
        "overdue": result[4] or 0,
        "due_today": 0,  # TODO: Calculate
        "due_this_week": 0  # TODO: Calculate
    }
