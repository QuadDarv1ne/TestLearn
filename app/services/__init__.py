"""
Сервисы для образовательной платформы TestLearn
"""
from app.services.gamification_service import CertificateService, LeaderboardService
from app.services.progress_service import ProgressService
from app.services.quiz_checker_service import QuizCheckerService
from app.services.search_service import RecommendationService, SearchService
from app.services.social_service import CommentService, NotificationService

__all__ = [
    "ProgressService",
    "SearchService",
    "RecommendationService",
    "LeaderboardService",
    "CertificateService",
    "CommentService",
    "NotificationService",
    "QuizCheckerService",
]
