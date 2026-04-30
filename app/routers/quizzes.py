"""
Quizzes API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any, Dict
from datetime import datetime, UTC

from app.db.database import get_db
from app.db.models import Quiz, Question, QuizResult, Category, UserProgress
from app.schemas import (
    QuizResponse, QuestionCreate, QuestionResponse,
    QuizResultResponse, QuizResultDetail, QuizSubmit, QuizAnswerSubmit
)
from app.services import QuizCheckerService, ProgressService

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


@router.get("/{quiz_id}/take", response_model=List[dict])
@router.get("/{quiz_id}/questions", response_model=List[dict])
def take_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get all questions for a quiz (without correct answers for taking the quiz).
    
    Supports multiple question types: single_choice, multiple_choice, true_false,
    short_answer, matching, ordering, fill_blank.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).order_by(Question.order_num).all()

    result = []
    for q in questions:
        q_data = {
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type or "single_choice",
            "order_num": q.order_num,
            "points": q.points,
        }
        
        # Include options based on question type
        if q.question_type in ["single_choice", "multiple_choice", None]:
            q_data["option_a"] = q.option_a
            q_data["option_b"] = q.option_b
            q_data["option_c"] = q.option_c
            q_data["option_d"] = q.option_d
        elif q.question_type == "true_false":
            q_data["option_a"] = "True"
            q_data["option_b"] = "False"
        elif q.question_type == "matching":
            q_data["matching_pairs"] = q.matching_pairs
        elif q.question_type == "ordering":
            q_data["ordering_items"] = q.ordering_items
        elif q.question_type in ["short_answer", "fill_blank"]:
            pass  # No options needed
        
        result.append(q_data)

    return result


@router.post("/{quiz_id}/submit", response_model=QuizResultDetail)
def submit_quiz(quiz_id: int, submission: QuizSubmit, db: Session = Depends(get_db)):
    """Submit quiz answers and get results with detailed feedback.
    
    Supports multiple question types with automatic grading and partial credit.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get all questions for this quiz
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    questions_map = {q.id: q for q in questions}
    
    # Grade each answer
    total_points = 0
    max_points = sum(q.points for q in questions)
    correct_count = 0
    question_results = []
    answers_dict = {}
    
    for answer_sub in submission.answers:
        question = questions_map.get(answer_sub.question_id)
        if not question:
            continue
        
        is_correct, points, explanation = QuizCheckerService.check_answer(
            question, answer_sub.answer
        )
        
        total_points += points
        if is_correct:
            correct_count += 1
        
        # Store user answer
        answers_dict[str(answer_sub.question_id)] = answer_sub.answer
        
        question_results.append({
            "question_id": answer_sub.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type or "single_choice",
            "is_correct": is_correct,
            "points_earned": points,
            "max_points": question.points,
            "user_answer": answer_sub.answer,
            "explanation": explanation
        })
    
    # Calculate score as percentage
    score = correct_count
    total = len(questions)
    
    # Create quiz result
    db_result = QuizResult(
        quiz_id=quiz_id,
        session_id=submission.session_id,
        score=score,
        total=total,
        total_points=total_points,
        answers=answers_dict
    )
    db.add(db_result)
    
    # Update user progress if session_id provided
    if submission.session_id:
        ProgressService.add_experience(submission.session_id, total_points, db)
        
        # Increment quizzes_passed if score >= 50%
        if total > 0 and (correct_count / total) >= 0.5:
            progress = db.query(UserProgress).filter(
                UserProgress.session_id == submission.session_id
            ).first()
            if progress:
                progress.quizzes_passed += 1
    
    db.commit()
    db.refresh(db_result)
    
    # Calculate percentage
    percentage = (score / total * 100) if total > 0 else 0
    
    return {
        "id": db_result.id,
        "quiz_id": db_result.quiz_id,
        "score": db_result.score,
        "total": db_result.total,
        "total_points": db_result.total_points,
        "answers": db_result.answers,
        "session_id": db_result.session_id,
        "created_at": db_result.created_at,
        "percentage": percentage,
        "question_results": question_results
    }


@router.get("/results/{result_id}", response_model=QuizResultDetail)
def get_quiz_result(result_id: str, db: Session = Depends(get_db)):
    """Get detailed quiz result by ID."""
    result = db.query(QuizResult).filter(QuizResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # Rebuild question results from stored answers
    questions = db.query(Question).filter(Question.quiz_id == result.quiz_id).all()
    question_results = []
    
    answers = result.answers or {}
    for q in questions:
        user_answer = answers.get(str(q.id))
        if user_answer is not None:
            is_correct, points, explanation = QuizCheckerService.check_answer(q, user_answer)
            question_results.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type or "single_choice",
                "is_correct": is_correct,
                "points_earned": points,
                "max_points": q.points,
                "user_answer": user_answer,
                "explanation": explanation
            })
    
    percentage = (result.score / result.total * 100) if result.total > 0 else 0
    
    return {
        "id": result.id,
        "quiz_id": result.quiz_id,
        "score": result.score,
        "total": result.total,
        "total_points": result.total_points,
        "answers": result.answers,
        "session_id": result.session_id,
        "created_at": result.created_at,
        "percentage": percentage,
        "question_results": question_results
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


@router.post("/questions", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question for a quiz (admin only).
    
    Supports multiple question types. Set question_type and provide appropriate fields.
    """
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=400, detail="Quiz not found")

    # Validate question type-specific fields
    q_type = question.question_type or "single_choice"
    
    if q_type == "single_choice":
        if question.correct_option not in ["A", "B", "C", "D"]:
            raise HTTPException(status_code=400, detail="Correct option must be A, B, C, or D")
    elif q_type == "multiple_choice":
        if not question.correct_option:
            raise HTTPException(status_code=400, detail="Correct option required (e.g., 'A,B,C')")
    elif q_type == "true_false":
        if question.is_true is None:
            raise HTTPException(status_code=400, detail="is_true field required for true/false questions")
    elif q_type in ["short_answer", "fill_blank"]:
        if not question.correct_answer:
            raise HTTPException(status_code=400, detail="correct_answer required for text-based questions")
    elif q_type == "matching":
        if not question.correct_matches:
            raise HTTPException(status_code=400, detail="correct_matches required for matching questions")
    elif q_type == "ordering":
        if not question.correct_order:
            raise HTTPException(status_code=400, detail="correct_order required for ordering questions")

    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return {
        "id": db_question.id,
        "question_text": db_question.question_text,
        "question_type": db_question.question_type,
        "option_a": db_question.option_a,
        "option_b": db_question.option_b,
        "option_c": db_question.option_c,
        "option_d": db_question.option_d,
        "is_true": db_question.is_true,
        "correct_answer": db_question.correct_answer,
        "correct_option": db_question.correct_option,
        "explanation": db_question.explanation or "",
        "quiz_id": db_question.quiz_id,
        "order_num": db_question.order_num,
        "points": db_question.points
    }
