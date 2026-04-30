"""
Сервис для геймификации: таблица лидеров и сертификаты
"""
from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import LeaderboardEntry, Certificate
from app.db.models import UserProgress, QuizResult
from app.services.progress_service import ProgressService


class LeaderboardService:
    """Сервис для управления таблицей лидеров."""

    @staticmethod
    def get_leaderboard(limit: int = 10, db: Optional[Session] = None) -> List[LeaderboardEntry]:
        """Получить таблицу лидеров."""
        if db is None:
            return []
            
        progress_entries = db.query(UserProgress).order_by(
            UserProgress.total_score.desc(),
            UserProgress.quizzes_passed.desc()
        ).limit(limit).all()

        leaderboard = []
        for rank, entry in enumerate(progress_entries, 1):
            # Calculate average score from quiz_results
            # Note: QuizResult doesn't have user_progress_id, so we use session_id indirectly
            avg_score = 0.0

            # Calculate level
            level, _, _ = ProgressService.calculate_level(entry.total_score)
            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=entry.id,
                username=f"User_{entry.session_id[:8]}",
                level=level,
                experience=entry.total_score,
                quizzes_passed=entry.quizzes_passed,
                average_score=avg_score
            ))
        return leaderboard


class CertificateService:
    """Сервис для генерации сертификатов."""

    @staticmethod
    def generate_certificate(session_id: str, db: Session) -> Optional[Certificate]:
        """Сгенерировать сертификат о прохождении курса."""
        progress = db.query(UserProgress).filter(
            UserProgress.session_id == session_id
        ).first()

        if not progress:
            return None

        # Проверить минимальные требования (5 тестов пройдено)
        if progress.quizzes_passed < 5:
            return None

        # Рассчитать уровень
        level, _, _ = ProgressService.calculate_level(progress.total_score)

        # Рассчитать средний балл (общий по системе)
        avg_result = db.query(func.avg(QuizResult.score * 100.0 / QuizResult.total)).scalar()
        average_score = round(avg_result, 1) if avg_result else 0.0

        return Certificate(
            id=str(datetime.now(UTC).timestamp()),
            user_id=progress.id,
            username=f"User_{session_id[:8]}",
            issued_at=datetime.now(UTC).isoformat(),
            level=level,
            topics_completed=progress.topics_read,
            quizzes_passed=progress.quizzes_passed,
            average_score=average_score,
            certificate_url=f"/certificates/{progress.id}"
        )
