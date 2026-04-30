"""
Сервисы для образовательной платформы TestLearn
"""
from app.services.progress_service import ProgressService
from app.services.search_service import SearchService, RecommendationService
from app.services.gamification_service import LeaderboardService, CertificateService
from app.services.social_service import CommentService, NotificationService

__all__ = [
    "ProgressService",
    "SearchService",
    "RecommendationService",
    "LeaderboardService",
    "CertificateService",
    "CommentService",
    "NotificationService",
]
