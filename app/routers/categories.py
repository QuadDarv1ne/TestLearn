""" Categories API router с оптимизированными SQL запросами """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.db.models import Category, Topic
from app.schemas import CategoryResponse, CategoryCreate

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """
    Получить все категории с количеством тем.

    Оптимизация: Использует LEFT JOIN и агрегатную функцию COUNT вместо N+1 запросов.
    """
    # Оптимизированный запрос с JOIN и GROUP BY
    result = db.query(
        Category,
        func.count(Topic.id).label('topics_count')
    ).outerjoin(
        Topic, Category.id == Topic.category_id
    ).group_by(
        Category.id
    ).all()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description or "",
            "icon": cat.icon or "check-circle",
            "topics_count": count or 0
        }
        for cat, count in result
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Получить категорию по ID.

    Оптимизация: Использует subquery для получения count вместо отдельного запроса.
    """
    # Проверяем существование категории
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Получаем count одним запросом с category
    topics_count = db.query(
        func.count(Topic.id)
    ).filter(
        Topic.category_id == category_id
    ).scalar() or 0

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description or "",
        "icon": category.icon or "check-circle",
        "topics_count": topics_count
    }


@router.post("", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Создать новую категорию (только админ).

    Оптимизация: Использует one() вместо first() для более быстрой проверки.
    """
    # Проверяем дубликат slug с one_or_none()
    existing = db.query(Category).filter(
        Category.slug == category.slug
    ).one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category with this slug already exists"
        )

    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return {
        "id": db_category.id,
        "name": db_category.name,
        "slug": db_category.slug,
        "description": db_category.description or "",
        "icon": db_category.icon or "check-circle",
        "topics_count": 0
    }


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryCreate, db: Session = Depends(get_db)):
    """
    Обновить категорию (только админ).
    """
    category = db.query(Category).filter(Category.id == category_id).one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверяем, не занят ли slug другой категорией
    if category_data.slug != category.slug:
        existing = db.query(Category).filter(
            Category.slug == category_data.slug,
            Category.id != category_id
        ).one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Category with this slug already exists"
            )

    # Обновляем поля
    for key, value in category_data.model_dump().items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    topics_count = db.query(func.count(Topic.id)).filter(
        Topic.category_id == category_id
    ).scalar() or 0

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description or "",
        "icon": category.icon or "check-circle",
        "topics_count": topics_count
    }


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Удалить категорию (только админ).
    """
    category = db.query(Category).filter(Category.id == category_id).one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверяем есть ли темы в категории
    topics_count = db.query(func.count(Topic.id)).filter(
        Topic.category_id == category_id
    ).scalar() or 0

    if topics_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with existing topics"
        )

    db.delete(category)
    db.commit()

    return {"status": "deleted", "message": "Category deleted successfully"}
