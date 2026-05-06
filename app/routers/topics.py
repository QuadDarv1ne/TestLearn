""" Topics API router с оптимизированными SQL запросами """
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.db.models import Bookmark, Category, ReadTopic, Topic
from app.schemas import TopicCreate, TopicResponse

router = APIRouter()


@router.get("", response_model=List[TopicResponse])
def get_topics(
    category_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Получить все темы с пагинацией и фильтрацией по категории.

    Оптимизация:
    - Использует joinedload для eager loading категорий
    - Добавлена пагинация для уменьшения объема данных
    - Фильтрация по category_id в WHERE вместо Python
    """
    query = db.query(Topic).join(Category).options(
        joinedload(Topic.category)
    )

    # Фильтрация по категории
    if category_id:
        query = query.filter(Topic.category_id == category_id)

    # Пагинация
    topics = query.order_by(
        Topic.order_num, Topic.title
    ).offset(offset).limit(limit).all()

    result = []
    for topic in topics:
        result.append({
            "id": topic.id,
            "title": topic.title,
            "content": topic.content,
            "category_id": topic.category_id,
            "order_num": topic.order_num,
            "category_name": topic.category.name if topic.category else None
        })

    return result


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Получить тему по ID.

    Оптимизация: Использует joinedload для получения категории одним запросом.
    """
    topic = db.query(Topic).options(
        joinedload(Topic.category)
    ).filter(Topic.id == topic_id).one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return {
        "id": topic.id,
        "title": topic.title,
        "content": topic.content,
        "category_id": topic.category_id,
        "order_num": topic.order_num,
        "category_name": topic.category.name if topic.category else None
    }


@router.post("", response_model=TopicResponse)
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    """Создать новую тему (только админ)."""
    # Проверяем категорию с one_or_none()
    category = db.query(Category).filter(
        Category.id == topic.category_id
    ).one_or_none()

    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    db_topic = Topic(**topic.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)

    return {
        "id": db_topic.id,
        "title": db_topic.title,
        "content": db_topic.content,
        "category_id": db_topic.category_id,
        "order_num": db_topic.order_num,
        "category_name": category.name
    }


@router.put("/{topic_id}", response_model=TopicResponse)
def update_topic(topic_id: int, topic_data: TopicCreate, db: Session = Depends(get_db)):
    """Обновить существующую тему (только админ)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Проверяем категорию
    category = db.query(Category).filter(
        Category.id == topic_data.category_id
    ).one_or_none()

    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    # Обновляем поля
    for key, value in topic_data.model_dump().items():
        setattr(topic, key, value)

    db.commit()
    db.refresh(topic)

    return {
        "id": topic.id,
        "title": topic.title,
        "content": topic.content,
        "category_id": topic.category_id,
        "order_num": topic.order_num,
        "category_name": category.name
    }


@router.delete("/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Удалить тему (только админ)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).one_or_none()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Удаляем связанные записи из read_topics и bookmarks
    db.query(ReadTopic).filter(ReadTopic.topic_id == topic_id).delete()
    db.query(Bookmark).filter(Bookmark.topic_id == topic_id).delete()

    db.delete(topic)
    db.commit()

    return {"status": "deleted"}


@router.get("/recommendations", response_model=List[TopicResponse])
def get_recommendations(
    request: Request,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Получить рекомендуемые темы для пользователя на основе прогресса.

    Оптимизация:
    - Использует subquery для получения прочитанных тем
    - Фильтрация на уровне БД вместо Python
    """
    session_id = request.cookies.get("session_id", "anonymous")

    if session_id != "anonymous":
        # Подзапрос для получения прочитанных тем
        read_topic_ids_subquery = db.query(ReadTopic.topic_id).filter(
            ReadTopic.session_id == session_id
        ).subquery()

        # Получаем непрочитанные темы
        topics = db.query(Topic).filter(
            ~Topic.id.in_(db.query(read_topic_ids_subquery))
        ).order_by(Topic.order_num, Topic.title).limit(limit).all()

        # Если все темы прочитаны, возвращаем случайные
        if not topics:
            topics = db.query(Topic).order_by(
                func.random()
            ).limit(limit).all()
    else:
        # Для анонимных пользователей возвращаем случайные темы
        topics = db.query(Topic).order_by(
            func.random()
        ).limit(limit).all()

    result = []
    for topic in topics:
        category = db.query(Category).filter(
            Category.id == topic.category_id
        ).one_or_none()
        result.append({
            "id": topic.id,
            "title": topic.title,
            "content": topic.content,
            "category_id": topic.category_id,
            "order_num": topic.order_num,
            "category_name": category.name if category else None
        })

    return result
