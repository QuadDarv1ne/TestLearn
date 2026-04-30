"""
Quizzes API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import Quiz, Question, QuizResult, Category
from app.schemas import QuizResponse, QuestionCreate, QuizResultResponse

router = APIRouter()


@router.get("", response_model=List[QuizResponse])
def get_quizzes(db: Session = Depends(get_db)):
    """Get all quizzes with question counts."""
    quizzes = db.query(Quiz).all()

    result = []
    for quiz in quizzes:
        questions_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()

        result.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description or "",
            "category_id": quiz.category_id,
            "questions_count": questions_count
        })

    return result


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a specific quiz by ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions_count = db.query(Question).filter(Question.quiz_id == quiz_id).count()

    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description or "",
        "category_id": quiz.category_id,
        "questions_count": questions_count
    }


@router.get("/{quiz_id}/questions", response_model=List[dict])
def get_quiz_questions(quiz_id: int, db: Session = Depends(get_db)):
    """Get all questions for a quiz (without correct answers for taking the quiz)."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.order_num).all()

    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "order_num": q.order_num
        })

    return result


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz_result(quiz_id: int, result_data: dict, db: Session = Depends(get_db)):
    """Submit quiz results."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    score = result_data.get("score", 0)
    total = result_data.get("total", 0)

    db_result = QuizResult(
        quiz_id=quiz_id,
        score=score,
        total=total
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    percentage = (score / total * 100) if total > 0 else 0

    return {
        "id": db_result.id,
        "quiz_id": db_result.quiz_id,
        "score": db_result.score,
        "total": db_result.total,
        "created_at": db_result.created_at,
        "percentage": percentage
    }


@router.post("", response_model=QuizResponse)
def create_quiz(title: str, description: str = "", category_id: int = None, db: Session = Depends(get_db)):
    """Create a new quiz (admin only)."""
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    db_quiz = Quiz(
        title=title,
        description=description,
        category_id=category_id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)

    return {
        "id": db_quiz.id,
        "title": db_quiz.title,
        "description": db_quiz.description or "",
        "category_id": db_quiz.category_id,
        "questions_count": 0
    }


@router.post("/questions", response_model=dict)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question for a quiz (admin only)."""
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=400, detail="Quiz not found")

    if question.correct_option not in ["A", "B", "C", "D"]:
        raise HTTPException(status_code=400, detail="Correct option must be A, B, C, or D")

    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return {
        "id": db_question.id,
        "question_text": db_question.question_text,
        "option_a": db_question.option_a,
        "option_b": db_question.option_b,
        "option_c": db_question.option_c,
        "option_d": db_question.option_d,
        "correct_option": db_question.correct_option,
        "explanation": db_question.explanation or "",
        "quiz_id": db_question.quiz_id,
        "order_num": db_question.order_num
    }
