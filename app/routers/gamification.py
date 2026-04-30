""" Router for gamification features: leaderboard, certificates, achievements """
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, UTC
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import UserProgress, QuizResult, Quiz
from app.schemas import LeaderboardEntry

router = APIRouter()


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get top users by total score."""
    progress_entries = db.query(UserProgress).order_by(
        UserProgress.total_score.desc(),
        UserProgress.quizzes_passed.desc()
    ).limit(limit).all()

    leaderboard = []
    for rank, entry in enumerate(progress_entries, 1):
        # Calculate level from experience
        level = 1
        xp_required = 100
        remaining_xp = entry.total_score
        while remaining_xp >= xp_required:
            remaining_xp -= xp_required
            level += 1
            xp_required = int(xp_required * 1.5)

        leaderboard.append(LeaderboardEntry(
            session_id=entry.session_id,
            total_score=entry.total_score,
            rank=rank
        ))

    return leaderboard


@router.get("/certificate")
def get_certificate(request: Request, db: Session = Depends(get_db)):
    """Generate certificate for user if eligible."""
    session_id = request.cookies.get("session_id", "anonymous")

    progress = db.query(UserProgress).filter(
        UserProgress.session_id == session_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="No progress found")

    # Check requirements: at least 5 quizzes passed
    if progress.quizzes_passed < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Need to pass at least 5 quizzes (current: {progress.quizzes_passed})"
        )

    # Calculate statistics
    results = db.query(QuizResult).all()
    avg_score = 0.0
    if results:
        total_percentage = sum(
            (r.score / r.total * 100) if r.total > 0 else 0 for r in results
        )
        avg_score = round(total_percentage / len(results), 1)

    # Calculate level
    level = 1
    xp_required = 100
    remaining_xp = progress.total_score
    while remaining_xp >= xp_required:
        remaining_xp -= xp_required
        level += 1
        xp_required = int(xp_required * 1.5)

    certificate_data = {
        "user_name": f"User_{session_id[:8]}",
        "course_name": "Software Testing Fundamentals",
        "completion_date": datetime.now(UTC).isoformat(),
        "score": avg_score,
        "level": level,
        "topics_completed": progress.topics_read,
        "quizzes_passed": progress.quizzes_passed
    }

    return certificate_data


@router.get("/achievements")
def get_achievements(request: Request, db: Session = Depends(get_db)):
    """Get user achievements based on progress."""
    session_id = request.cookies.get("session_id", "anonymous")

    progress = db.query(UserProgress).filter(
        UserProgress.session_id == session_id
    ).first()

    if not progress:
        return []

    achievements = [
        {
            "id": 1,
            "name": "Первые шаги",
            "description": "Прочитать первую тему",
            "icon": "📚",
            "unlocked": progress.topics_read >= 1
        },
        {
            "id": 2,
            "name": "Любопытный",
            "description": "Прочитать 5 тем",
            "icon": "🔍",
            "unlocked": progress.topics_read >= 5
        },
        {
            "id": 3,
            "name": "Эрудит",
            "description": "Прочитать 10 тем",
            "icon": "🎓",
            "unlocked": progress.topics_read >= 10
        },
        {
            "id": 4,
            "name": "Новичок в тестировании",
            "description": "Пройти первый тест",
            "icon": "✅",
            "unlocked": progress.quizzes_passed >= 1
        },
        {
            "id": 5,
            "name": "Опытный тестировщик",
            "description": "Пройти 5 тестов",
            "icon": "🏆",
            "unlocked": progress.quizzes_passed >= 5
        },
        {
            "id": 6,
            "name": "Мастер тестирования",
            "description": "Набрать 100+ баллов",
            "icon": "👑",
            "unlocked": progress.total_score >= 100
        }
    ]

    return achievements


@router.get("/daily-challenge")
def get_daily_challenge(db: Session = Depends(get_db)):
    """Get daily challenge (random quiz with bonus XP)."""
    # Get random quiz
    quiz = db.query(Quiz).order_by(func.random()).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="No quizzes available")

    expires = datetime.now(UTC).replace(hour=23, minute=59, second=59)

    return {
        "id": 1,
        "quiz_id": quiz.id,
        "title": "Ежедневный вызов",
        "description": "Пройдите тест и получите 50 XP!",
        "bonus_xp": 50,
        "completed": False,
        "expires_at": expires.isoformat()
    }
