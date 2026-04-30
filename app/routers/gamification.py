""" Router for gamification features: leaderboard, certificates, achievements """
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, UTC
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import UserProgress, QuizResult, Quiz, AchievementDefinition, UserAchievement
from app.schemas import LeaderboardEntry
from app.services import ProgressService

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

    # Используем сервис для получения достижений
    achievements = ProgressService.get_achievements(session_id, db)
    
    # Проверяем и разблокируем новые достижения
    newly_unlocked = ProgressService.check_and_unlock_achievements(session_id, db)
    
    return achievements


@router.post("/achievements/check")
def check_achievements(request: Request, db: Session = Depends(get_db)):
    """Check and unlock new achievements for the user."""
    session_id = request.cookies.get("session_id", "anonymous")
    
    newly_unlocked = ProgressService.check_and_unlock_achievements(session_id, db)
    
    return {
        "newly_unlocked": [
            {
                "id": ach.id,
                "name": ach.name,
                "description": ach.description,
                "icon": ach.icon,
                "unlocked_at": ach.unlocked_at
            }
            for ach in newly_unlocked
        ],
        "count": len(newly_unlocked)
    }


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
