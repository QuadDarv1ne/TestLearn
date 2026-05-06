"""
API routers for TestLearn application
"""
from fastapi import APIRouter

from app.routers import (
    auth,
    categories,
    feedback,
    gamification,
    glossary,
    progress,
    quizzes,
    social,
    topics,
)

api_router = APIRouter()

api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(glossary.router, prefix="/glossary", tags=["glossary"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
