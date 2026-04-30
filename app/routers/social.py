"""Router for social features: comments and notifications."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.db.models import Topic
from app.schemas import CommentCreate, CommentResponse
from app.services.social_service import CommentService

router = APIRouter()


@router.get("/topics/{topic_id}/comments", response_model=List[CommentResponse])
def get_comments(topic_id: int, db: Session = Depends(get_db)):
    """Get all comments for a topic."""
    comments = CommentService.get_comments(topic_id, db)
    if comments is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return comments


@router.post("/comments", response_model=CommentResponse)
def add_comment(comment_data: CommentCreate, request: Request, db: Session = Depends(get_db)):
    """Add a comment to a topic."""
    # Get or create session ID for user identification
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))

    comment = CommentService.add_comment(
        topic_id=comment_data.topic_id,
        user_id=session_id,
        content=comment_data.content,
        db=db
    )

    if comment is None:
        # Check if topic exists
        from app.db.database import SessionLocal
        db_check = SessionLocal()
        try:
            topic = db_check.query(Topic).filter(Topic.id == comment_data.topic_id).first()
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found")
        finally:
            db_check.close()

        raise HTTPException(status_code=400, detail="Invalid comment content")

    return comment


@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: str, db: Session = Depends(get_db)):
    """Like a comment."""
    success = CommentService.like_comment(comment_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "success"}


@router.get("/notifications")
def get_notifications(request: Request, db: Session = Depends(get_db)):
    """Get unread notifications for user."""
    from app.db.database import SessionLocal
    from app.db.models import Notification

    session_id = request.cookies.get("session_id", "anonymous")
    notifications = db.query(Notification).filter(
        Notification.user_id == session_id,
        Notification.is_read.is_(False)
    ).order_by(Notification.created_at.desc()).limit(20).all()

    return notifications


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """Mark notification as read."""
    from app.db.database import SessionLocal
    from app.db.models import Notification

    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    return {"status": "success"}
