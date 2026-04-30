""" Health check and system status endpoints """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from app.db.database import get_db
from app.db.models import Category, Topic, Quiz, Question, GlossaryTerm, Feedback, UserProgress

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if the application is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "TestLearn API"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with database connectivity and statistics.
    Returns comprehensive system status.
    """
    try:
        # Test database connection
        db.execute(db.connection().connection.cursor().execute("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    try:
        # Get database statistics
        stats = {
            "categories": db.query(Category).count(),
            "topics": db.query(Topic).count(),
            "quizzes": db.query(Quiz).count(),
            "questions": db.query(Question).count(),
            "glossary_terms": db.query(GlossaryTerm).count(),
            "feedback": db.query(Feedback).count(),
            "user_progress": db.query(UserProgress).count()
        }
    except Exception as e:
        stats = {"error": str(e)}

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "TestLearn API",
        "version": "2.0.0",
        "database": {
            "status": db_status,
            "statistics": stats
        },
        "uptime": {
            "started_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - determines if the application is ready to serve requests.
    Used by Kubernetes and other orchestration systems.
    """
    try:
        # Check database connection
        db.query(Category).count()
        return {"ready": True, "timestamp": datetime.now(UTC).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/live")
async def liveness_check():
    """
    Liveness check - determines if the application is running.
    Used by Kubernetes to determine if the pod should be restarted.
    """
    return {"alive": True, "timestamp": datetime.now(UTC).isoformat()}


@router.get("/info")
async def get_app_info():
    """
    Application information endpoint.
    Returns metadata about the application.
    """
    return {
        "name": "TestLearn — Educational Platform for Software Testing",
        "version": "2.0.0",
        "description": "Учебная платформа по основам тестирования программного обеспечения",
        "author": "Самойлов Д.А.",
        "institution": "МФЮА",
        "technology_stack": {
            "backend": "FastAPI",
            "database": "SQLite",
            "frontend": "Jinja2 + Tailwind CSS"
        },
        "features": [
            "Теория по тестированию ПО",
            "Интерактивные тесты",
            "Глоссарий терминов",
            "Отслеживание прогресса",
            "Геймификация",
            "Социальные функции"
        ]
    }
