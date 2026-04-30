"""
Router for social features: comments and notifications
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, UTC
import uuid

from app.db.database import get_db
from app.db.models import Comment, Notification, Topic
from app.schemas import CommentCreate, CommentResponse

router = APIRouter()


@router.get("/topics/{topic_id}/comments", response_model=List[CommentResponse])
def get_comments(topic_id: int, db: Session = Depends(get_db)):
    """Get all comments for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    comments = db.query(Comment).filter(
        Comment.topic_id == topic_id
    ).order_by(Comment.created_at.desc()).all()

    return comments


@router.post("/comments", response_model=CommentResponse)
def add_comment(comment_data: CommentCreate, request: Request, db: Session = Depends(get_db)):
    """Add a comment to a topic."""
    topic = db.query(Topic).filter(Topic.id == comment_data.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get or create session ID for user identification
    session_id = request.cookies.get("session_id", str(uuid.uuid4()))

    comment = Comment(
        id=str(uuid.uuid4()),
        topic_id=comment_data.topic_id,
        user_id=session_id,
        content=comment_data.content,
        created_at=datetime.now(UTC),
        likes=0
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: str, db: Session = Depends(get_db)):
    """Like a comment."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.likes += 1
    db.commit()

    return {"status": "success", "likes": comment.likes}


@router.get("/notifications")
def get_notifications(request: Request, db: Session = Depends(get_db)):
    """Get unread notifications for user."""
    session_id = request.cookies.get("session_id", "anonymous")

    notifications = db.query(Notification).filter(
        Notification.user_id == session_id,
        Notification.is_read.is_(False)
    ).order_by(Notification.created_at.desc()).limit(20).all()

    return notifications


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """Mark notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()

    return {"status": "success"}
