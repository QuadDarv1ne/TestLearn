""" Frontend pages router """
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime

from app.db.database import get_db
from app.db.models import Topic, Category, ReadTopic, User, Quiz, Question, GlossaryTerm

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/topic/{topic_id}", include_in_schema=False)
async def topic_page(request: Request, topic_id: int):
    """Страница отдельной темы."""
    db: Session = next(get_db())
    try:
        # Get topic with category
        topic = db.query(Topic).options(
            joinedload(Topic.category)
        ).filter(Topic.id == topic_id).one_or_none()

        if not topic:
            raise HTTPException(status_code=404, detail="Тема не найдена")

        # Get session_id from cookie
        session_id = request.cookies.get("session_id", "anonymous")

        # Check if user has read this topic
        is_read = db.query(ReadTopic).filter(
            ReadTopic.topic_id == topic_id,
            ReadTopic.session_id == session_id
        ).first() is not None

        # Mark as read if not already read
        if not is_read and session_id != "anonymous":
            read_topic = ReadTopic(
                topic_id=topic_id,
                session_id=session_id,
                read_at=datetime.utcnow()
            )
            db.add(read_topic)
            db.commit()

        # Get next/prev topics for navigation
        next_topic = db.query(Topic).filter(
            Topic.order_num > topic.order_num,
            Topic.category_id == topic.category_id
        ).order_by(Topic.order_num).first()

        prev_topic = db.query(Topic).filter(
            Topic.order_num < topic.order_num,
            Topic.category_id == topic.category_id
        ).order_by(Topic.order_num.desc()).first()

        return templates.TemplateResponse("topic.html", {
            "request": request,
            "topic": topic,
            "category_name": topic.category.name if topic.category else "Unknown",
            "formatted_content": topic.content,
            "is_read": is_read,
            "next_topic": next_topic,
            "prev_topic": prev_topic
        })
    finally:
        db.close()
