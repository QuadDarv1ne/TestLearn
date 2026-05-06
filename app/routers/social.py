"""Router for social features: comments and notifications."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Topic
from app.schemas import CommentCreate, CommentResponse
from app.services.social_service import CommentService

router = APIRouter()

@router.get("/topics/{topic_id}/comments")
def get_comments(
    topic_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get comments for a topic with pagination.
    
    Returns paginated list of comments with metadata.
    """
    result = CommentService.get_comments(
        topic_id=topic_id,
        db=db,
        limit=page_size,
        offset=(page - 1) * page_size
    )
    return result

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
def get_notifications(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get unread notifications for user with pagination.
    
    Returns paginated list of unread notifications with metadata.
    """
    from app.services.social_service import NotificationService

    session_id = request.cookies.get("session_id", "anonymous")

    result = NotificationService.get_unread_notifications(
        user_id=session_id,
        db=db,
        limit=page_size,
        offset=(page - 1) * page_size
    )
    return result

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """Mark notification as read."""
    from app.db.models import Notification
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return {"status": "success"}
