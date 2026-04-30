"""
Glossary API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import GlossaryTerm
from app.schemas import GlossaryTermResponse, GlossaryTermCreate

router = APIRouter()


@router.get("", response_model=List[GlossaryTermResponse])
def get_glossary(db: Session = Depends(get_db)):
    """Get all glossary terms."""
    terms = db.query(GlossaryTerm).order_by(GlossaryTerm.letter, GlossaryTerm.term).all()

    return [
        {
            "id": t.id,
            "term": t.term,
            "definition": t.definition,
            "letter": t.letter
        }
        for t in terms
    ]


@router.get("/{term_id}", response_model=GlossaryTermResponse)
def get_term(term_id: int, db: Session = Depends(get_db)):
    """Get a specific term by ID."""
    term = db.query(GlossaryTerm).filter(GlossaryTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")

    return {
        "id": term.id,
        "term": term.term,
        "definition": term.definition,
        "letter": term.letter
    }


@router.post("", response_model=GlossaryTermResponse)
def create_term(term: GlossaryTermCreate, db: Session = Depends(get_db)):
    """Create a new glossary term (admin only)."""
    # Check if term already exists
    existing = db.query(GlossaryTerm).filter(GlossaryTerm.term == term.term).first()
    if existing:
        raise HTTPException(status_code=400, detail="Term already exists")

    db_term = GlossaryTerm(**term.model_dump())
    db.add(db_term)
    db.commit()
    db.refresh(db_term)

    return {
        "id": db_term.id,
        "term": db_term.term,
        "definition": db_term.definition,
        "letter": db_term.letter
    }
