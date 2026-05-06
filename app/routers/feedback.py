"""
Feedback API router
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Feedback as FeedbackModel
from app.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.get("", response_model=List[FeedbackResponse])
def get_feedback(db: Session = Depends(get_db)):
    """Get all feedback entries."""
    feedback_list = db.query(FeedbackModel).order_by(FeedbackModel.created_at.desc()).all()

    return [
        {
            "id": f.id,
            "name": f.name,
            "email": f.email or "",
            "message": f.message,
            "rating": f.rating,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in feedback_list
    ]


@router.post("", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit new feedback."""
    import uuid
    from datetime import UTC, datetime

    db_feedback = FeedbackModel(
        id=str(uuid.uuid4()),
        name=feedback.name,
        email=feedback.email or "",
        message=feedback.message,
        rating=feedback.rating,
        created_at=datetime.now(UTC)
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return {
        "id": db_feedback.id,
        "name": db_feedback.name,
        "email": db_feedback.email or "",
        "message": db_feedback.message,
        "rating": db_feedback.rating,
        "created_at": db_feedback.created_at.isoformat() if db_feedback.created_at else None
    }
