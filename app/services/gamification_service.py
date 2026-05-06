""" Сервис для геймификации: таблица лидеров и сертификаты """
from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import QuizResult, UserProgress
from app.models import Certificate, LeaderboardEntry
from app.services.progress_service import ProgressService


class LeaderboardService:
    """Сервис для управления таблицей лидеров."""

    @staticmethod
    def get_leaderboard(limit: int = 10, offset: int = 0, db: Optional[Session] = None) -> List[LeaderboardEntry]:
        """
        Получить таблицу лидеров с пагинацией.
        
        Args:
            limit: Максимальное количество записей (по умолчанию 10)
            offset: Смещение для пагинации (по умолчанию 0)
            db: Сессия базы данных
            
        Returns:
            Список записей таблицы лидеров
        """
        if db is None:
            return []

        # Проверка на None для offset
        if offset is None:
            offset = 0

        # Проверка на None для limit
        if limit is None:
            limit = 10

        progress_entries = db.query(UserProgress).order_by(
            UserProgress.total_score.desc(),
            UserProgress.quizzes_passed.desc()
        ).offset(offset).limit(limit).all()

        leaderboard = []
        base_rank = offset + 1

        for rank, entry in enumerate(progress_entries, start=base_rank):
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

    @staticmethod
    def get_leaderboard_page(page: int = 1, page_size: int = 10, db: Optional[Session] = None) -> dict:
        """
        Получить страницу таблицы лидеров с метаданными пагинации.
        
        Args:
            page: Номер страницы (начинается с 1)
            page_size: Количество записей на странице
            db: Сессия базы данных
            
        Returns:
            Словарь с записями и метаданными пагинации
        """
        if db is None:
            return {"items": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0}

        # Валидация параметров
        if page is None or page < 1:
            page = 1
        if page_size is None or page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100

        offset = (page - 1) * page_size

        # Получаем общее количество записей
        total = db.query(UserProgress).count()
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # Получаем записи для текущей страницы
        items = LeaderboardService.get_leaderboard(
            limit=page_size,
            offset=offset,
            db=db
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

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
