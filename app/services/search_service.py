"""
Сервис для поиска и рекомендаций
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Category, GlossaryTerm, ReadTopic, Topic
from app.models import SearchResults


class SearchService:
    """Сервис для поиска по материалам."""

    @staticmethod
    def search(query: str, db: Session) -> SearchResults:
        """Поиск по темам и глоссарию."""
        search_term = f"%{query}%"

        # Поиск по темам
        topics_query = db.query(Topic, Category.name.label('category_name'))\
            .join(Category, Topic.category_id == Category.id)\
            .filter(
                (Topic.title.ilike(search_term)) |
                (Topic.content.ilike(search_term))
            )\
            .limit(10)\
            .all()

        topics = [
            {
                "id": topic.id,
                "title": topic.title,
                "snippet": topic.content[:200] + "...",
                "category": category_name
            }
            for topic, category_name in topics_query
        ]

        # Поиск по глоссарию
        glossary_terms = db.query(GlossaryTerm).filter(
            (GlossaryTerm.term.ilike(search_term)) |
            (GlossaryTerm.definition.ilike(search_term))
        ).limit(10).all()

        glossary_results = [
            {
                "id": term.id,
                "term": term.term,
                "definition": term.definition
            }
            for term in glossary_terms
        ]

        return SearchResults(
            topics=topics,
            glossary_terms=glossary_results,
            query=query,
            total_results=len(topics) + len(glossary_results)
        )


class RecommendationService:
    """Сервис для рекомендаций контента."""

    @staticmethod
    def get_recommendations(session_id: str, limit: int = 3, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Получить рекомендации тем для изучения."""
        # Получить категории, которые пользователь ещё не изучал
        unread_categories = db.query(Category.id, Category.name).filter(
            Category.id.notin_(
                db.query(Topic.category_id).join(
                    ReadTopic, Topic.id == ReadTopic.topic_id
                ).filter(ReadTopic.session_id == session_id)
            )
        ).limit(limit).all()

        if not unread_categories:
            # Если все категории изучены, вернуть случайные темы
            recommendations = db.query(Topic, Category.name.label('category_name'))\
                .join(Category, Topic.category_id == Category.id)\
                .order_by(func.random())\
                .limit(limit)\
                .all()
            return [
                {
                    "id": topic.id,
                    "category_id": topic.category_id,
                    "title": topic.title,
                    "content": topic.content,
                    "order_num": topic.order_num,
                    "category_name": category_name
                }
                for topic, category_name in recommendations
            ]
        else:
            # Вернуть темы из непрочитанных категорий
            category_ids = [cat.id for cat in unread_categories]
            recommendations = db.query(Topic, Category.name.label('category_name'))\
                .join(Category, Topic.category_id == Category.id)\
                .filter(
                    Topic.category_id.in_(category_ids),
                    Topic.id.notin_(
                        db.query(ReadTopic.topic_id).filter(
                            ReadTopic.session_id == session_id
                        )
                    )
                )\
                .order_by(Topic.order_num)\
                .limit(limit)\
                .all()
            return [
                {
                    "id": topic.id,
                    "category_id": topic.category_id,
                    "title": topic.title,
                    "content": topic.content,
                    "order_num": topic.order_num,
                    "category_name": category_name
                }
                for topic, category_name in recommendations
            ]
