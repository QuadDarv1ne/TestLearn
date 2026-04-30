""" Search API router for TestLearn platform """
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.db.models import Topic, Category, GlossaryTerm

router = APIRouter()


@router.get("/search", response_model=Dict[str, Any])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Search across topics and glossary terms.

    Returns matching results from both categories.
    """
    if not q or len(q) < 2:
        return {
            "topics": [],
            "glossary_terms": [],
            "query": q,
            "total_results": 0
        }

    search_term = f"%{q}%"

    # Search in topics
    topics_query = db.query(Topic, Category.name.label('category_name'))\
        .join(Category, Topic.category_id == Category.id)\
        .filter(
            (Topic.title.ilike(search_term)) | (Topic.content.ilike(search_term))
        )\
        .limit(10)\
        .all()

    topics = [
        {
            "id": topic.id,
            "title": topic.title,
            "snippet": topic.content[:200] + "..." if len(topic.content) > 200 else topic.content,
            "category": category_name
        }
        for topic, category_name in topics_query
    ]

    # Search in glossary
    glossary_terms = db.query(GlossaryTerm).filter(
        (GlossaryTerm.term.ilike(search_term)) | (GlossaryTerm.definition.ilike(search_term))
    ).limit(10).all()

    glossary_results = [
        {
            "id": term.id,
            "term": term.term,
            "definition": term.definition
        }
        for term in glossary_terms
    ]

    return {
        "topics": topics,
        "glossary_terms": glossary_results,
        "query": q,
        "total_results": len(topics) + len(glossary_results)
    }
