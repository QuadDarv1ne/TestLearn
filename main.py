"""
FastAPI приложение: Учебная платформа по основам тестирования программного обеспечения

Улучшенная версия с модульной архитектурой, SQLAlchemy и безопасной аутентификацией

Версия: 2.2.0
Описание: Образовательная платформа для изучения основ тестирования ПО с геймификацией
          и социальными функциями.

API Documentation:
    - Swagger UI: /api/docs
    - ReDoc: /api/redoc
    - OpenAPI: /api/openapi.json

Автор: Самойлов Д.А.
Организация: Московский областной филиал МФЮА
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import logging
from typing import Union
import time
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Импорт роутеров
from app.routers import auth, categories, topics, quizzes, glossary, feedback, progress, gamification, social, health, search, pages
from app.db.database import engine, Base
from app.db import models  # Импортируем модели для регистрации в Alembic
from app.services import LeaderboardService
from app.services.progress_service import ProgressService
from app.services.search_service import SearchService, RecommendationService
from app.services.gamification_service import CertificateService
from app.services.social_service import CommentService, NotificationService
from app.middleware.rate_limit import configure_rate_limiting, limiter, _rate_limit_exceeded_handler
from app.utils.cache import cache

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler для инициализации БД при запуске."""
    # Создание таблиц при старте (для совместимости)
    Base.metadata.create_all(bind=engine)

    # Заполнение начальными данными
    try:
        from app.services.progress_service import seed_initial_data
        seed_initial_data()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    yield

    # Очистка при завершении (если нужно)
    logger.info("Application shutdown")


app = FastAPI(
    title="TestLearn — Основы тестирования ПО",
    description="""
## Учебная платформа по основам тестирования программного обеспечения

### Основные возможности:
- 📚 **Теория**: 16 тем по 5 категориям тестирования
- 📝 **Викторины**: Интерактивные тесты с автоматической проверкой
- 📖 **Глоссарий**: 43 термина с поиском и фильтрацией
- 🏆 **Геймификация**: Уровни, достижения, таблица лидеров
- 💬 **Социальные функции**: Комментарии, уведомления
- 📊 **Статистика**: Отслеживание прогресса и экспорт данных

### API Endpoints:
- `/api/auth/*` — Аутентификация и авторизация
- `/api/categories/*` — Управление категориями
- `/api/topics/*` — Управление темами
- `/api/quizzes/*` — Управление викторинами и вопросами
- `/api/glossary/*` — Управление глоссарием
- `/api/feedback/*` — Обратная связь от пользователей
- `/api/progress/*` — Отслеживание прогресса
- `/api/leaderboard` — Таблица лидеров
- `/api/achievements` — Достижения пользователя
- `/api/search` — Поиск по материалам
- `/api/health/*` — Health check endpoints

### Геймификация:
- **Уровни**: От 1 до 50, растут с получением опыта
- **Опыт (XP)**: Начисляется за чтение тем и прохождение тестов
- **Достижения**: 10+ достижений за различные активности
- **Ежедневные вызовы**: Новые задания каждый день
- **Таблица лидеров**: Соревнуйтесь с другими пользователями

### Rate Limiting:
- **Общий лимит**: 100 запросов в минуту
- **API лимит**: 60 запросов в минуту
- **Аутентификация**: 10 запросов в минуту
- **Поиск**: 30 запросов в минуту
- **Обратная связь**: 20 запросов в минуту
    """,
    version="2.3.14",
    contact={
        "name": "Самойлов Д.А.",
        "email": "samoilov@example.com",
        "url": "https://github.com/QuadDarv1ne/TestLearn",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка rate limiting
configure_rate_limiting(app)

# Добавляем limiter к зависимостям по умолчанию
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Подключение роутеров с rate limiting
@app.get("/api/test", tags=["System"])
@limiter.limit("10/minute")
async def test_rate_limit(request: Request):
    """Тестовый endpoint с rate limiting."""
    return {"message": "Rate limiting is working"}


app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(glossary.router, prefix="/api/glossary", tags=["Glossary"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(gamification.router, prefix="/api", tags=["Gamification"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(health.router, prefix="/api", tags=["System"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(pages.router, tags=["Pages"])

# Обработчики глобальных ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": exc.status_code}
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Обработчик ошибок SQLAlchemy."""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred", "status": 500}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик всех остальных исключений."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status": 500}
    )


# Frontend pages
@app.get("/theory", include_in_schema=False)
async def theory_page(request: Request):
    """Теория раздел."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import Category, Topic

    db: Session = next(get_db())
    try:
        # Get all categories (ordered by name)
        categories = db.query(Category).order_by(Category.name).all()

        # Get all topics
        topics = db.query(Topic).order_by(Topic.order_num, Topic.title).all()

        # Organize topics by category
        topics_by_category = {}
        for topic in topics:
            if topic.category_id not in topics_by_category:
                topics_by_category[topic.category_id] = []
            topics_by_category[topic.category_id].append(topic)

        # Get all topic titles for datalist
        all_topic_titles = [topic.title for topic in topics]

        # For now, assume no topics read (would be user-specific in real app)
        topics_read = 0
        total_topics = len(topics)

        # Get query parameters
        query_params = dict(request.query_params)
        active_category_id = int(query_params.get("category_id", 0)) if query_params.get("category_id") else None
        search_query = query_params.get("search", "")

        return templates.TemplateResponse(request, "theory.html", {
            "categories": categories,
            "topics_by_category": topics_by_category,
            "all_topic_titles": all_topic_titles,
            "topics_read": topics_read,
            "total_topics": total_topics,
            "active_category_id": active_category_id,
            "search_query": search_query
        })
    finally:
        db.close()


@app.get("/topic/{topic_id}", include_in_schema=False)
async def topic_page(request: Request, topic_id: int):
    """Страница отдельной темы."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import Topic, Category, ReadTopic, User
    from datetime import datetime

    db: Session = next(get_db())
    try:
        # Get topic with category
        topic = db.query(Topic).options(
            joinedload(Topic.category)
        ).filter(Topic.id == topic_id).one_or_none()

        if not topic:
            raise HTTPException(status_code=404, detail="Тема не найдена")

        # Get session_id from cookie
        session_id = request.cookies.get("session_id", "anonymous")

        # Check if user has read this topic
        is_read = db.query(ReadTopic).filter(
            ReadTopic.topic_id == topic_id,
            ReadTopic.session_id == session_id
        ).first() is not None

        # Mark as read if not already read
        if not is_read and session_id != "anonymous":
            read_topic = ReadTopic(
                topic_id=topic_id,
                session_id=session_id,
                read_at=datetime.utcnow()
            )
            db.add(read_topic)

            # Update user progress
            user = db.query(User).filter(User.session_id == session_id).first()
            if user:
                user.progress.topics_read += 1
                # Add XP for reading topic
                from app.services.gamification_service import GamificationService
                GamificationService.add_xp(user, 10, db)
            db.commit()

        # Get next topic for navigation
        next_topic = db.query(Topic).filter(
            Topic.order_num > topic.order_num,
            Topic.category_id == topic.category_id
        ).order_by(Topic.order_num).first()

        # Get previous topic
        prev_topic = db.query(Topic).filter(
            Topic.order_num < topic.order_num,
            Topic.category_id == topic.category_id
        ).order_by(Topic.order_num.desc()).first()

        return templates.TemplateResponse(request, "topic.html", {
            "topic": topic,
            "category": topic.category,
            "is_read": is_read,
            "next_topic": next_topic,
            "prev_topic": prev_topic
        })
    finally:
        db.close()


@app.get("/quiz", include_in_schema=False)
async def quiz_page(request: Request):
    """Тесты раздел."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import Quiz, Question

    db: Session = next(get_db())
    try:
        # Get the first quiz available (or create a default one if none)
        quiz = db.query(Quiz).first()

        if not quiz:
            # If no quiz exists, we'll create a placeholder for demonstration
            # In a real app, you might redirect to a create quiz page or show a message
            quiz = Quiz(id=0, title="Доступные тесты", description="Пока нет доступных тестов")
            questions = []
        else:
            # Get questions for this quiz
            questions = db.query(Question).filter(Question.quiz_id == quiz.id).order_by(Question.order_num).all()

            # Convert to list of dicts for template
            questions = [{
                "id": q.id,
                "question_text": q.question_text,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d
            } for q in questions]

        # Set a default time limit (15 minutes in seconds)
        time_limit = 900

        return templates.TemplateResponse(request, "quiz.html", {
            "quiz": quiz,
            "questions": questions,
            "time_limit": time_limit
        })
    finally:
        db.close()


@app.get("/glossary", include_in_schema=False)
async def glossary_page(request: Request):
    """Глоссарий раздел."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import GlossaryTerm

    db: Session = next(get_db())
    try:
        # Get query parameters
        query_params = dict(request.query_params)
        active_letter = query_params.get("letter", "")
        search_query = query_params.get("search", "")

        # Build query
        query = db.query(GlossaryTerm)

        # Filter by letter if provided
        if active_letter:
            query = query.filter(GlossaryTerm.letter == active_letter.upper())

        # Filter by search query if provided
        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                (GlossaryTerm.term.ilike(search_term)) |
                (GlossaryTerm.definition.ilike(search_term))
            )

        # Get terms
        terms = query.order_by(GlossaryTerm.term).all()

        # Get all distinct letters for navigation
        all_letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]

        return templates.TemplateResponse(request, "glossary.html", {
            "terms": terms,
            "all_letters": all_letters,
            "active_letter": active_letter,
            "search_query": search_query
        })
    finally:
        db.close()


@app.get("/stats", include_in_schema=False)
async def stats_page(request: Request):
    """Статистика раздел."""
    # Try to get cached stats
    cached_stats = cache.get("stats_page")
    if cached_stats is not None:
        return templates.TemplateResponse(request, "stats.html", cached_stats)

    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import UserProgress, Topic, Category, QuizResult, Quiz
    from sqlalchemy import func

    db: Session = next(get_db())
    try:
        # Get or create user progress (using a default session for simplicity)
        session_id = 'default_session'
        progress = db.query(UserProgress).filter(UserProgress.session_id == session_id).first()

        if progress is None:
            # Create a temporary progress object with zeros
            class Progress:
                topics_read = 0
                quizzes_passed = 0
                total_score = 0
            progress = Progress()

        # Get total topics
        total_topics = db.query(Topic).count()

        # Get categories with topic count
        categories_with_stats = db.query(Category, func.count(Topic.id).label('topic_count'))\
            .outerjoin(Topic, Category.id == Topic.category_id)\
            .group_by(Category.id)\
            .all()

        # Convert to list of objects with name and topic_count attributes
        categories_with_stats = [{'name': cat.Category.name, 'topic_count': cat.topic_count} for cat in categories_with_stats]

        # Get total quiz results
        total_results = db.query(QuizResult).count()

        # Get average score percentage
        avg_score_result = db.query(func.avg(QuizResult.score * 100.0 / QuizResult.total)).scalar()
        avg_score = round(avg_score_result) if avg_score_result is not None else 0

        # Get total quizzes
        total_quizzes = db.query(Quiz).count()

        # Get score distribution (ranges: 0-49, 50-69, 70-89, 90-100)
        score_distribution = []
        ranges = [(0, 49), (50, 69), (70, 89), (90, 100)]
        for min_score, max_score in ranges:
            count = db.query(QuizResult).filter(
                (QuizResult.score * 100.0 / QuizResult.total) >= min_score,
                (QuizResult.score * 100.0 / QuizResult.total) <= max_score
            ).count()
            score_distribution.append({
                'range_label': f'{min_score}-{max_score}%',
                'count': count
            })

        # Get top results (top 5 by score percentage)
        top_results_query = db.query(QuizResult, Quiz.title.label('quiz_title'))\
            .join(Quiz, QuizResult.quiz_id == Quiz.id)\
            .order_by((QuizResult.score * 100.0 / QuizResult.total).desc())\
            .limit(5)\
            .all()

        top_results = []
        for result, quiz_title in top_results_query:
            percentage = int((result.score / result.total * 100)) if result.total > 0 else 0
            top_results.append({
                'quiz_title': quiz_title,
                'score': result.score,
                'total': result.total,
                'created_at': result.created_at.strftime('%Y-%m-%d') if result.created_at else '',
                'percentage': percentage
            })

        # Prepare context for template
        context = {
            "progress": progress,
            "total_topics": total_topics,
            "categories_with_stats": categories_with_stats,
            "total_results": total_results,
            "avg_score": avg_score,
            "total_quizzes": total_quizzes,
            "score_distribution": score_distribution,
            "top_results": top_results
        }

        # Cache the context for 60 seconds
        cache.set("stats_page", context, ttl=60)

        return templates.TemplateResponse(request, "stats.html", context)
    finally:
        db.close()


@app.get("/bookmarks", include_in_schema=False)
async def bookmarks_page(request: Request):
    """Закладки раздел."""
    return templates.TemplateResponse(request, "bookmarks.html", {})


@app.get("/database", include_in_schema=False)
async def database_page(request: Request):
    """База данных раздел."""
    from sqlalchemy import text
    from sqlalchemy.orm import Session
    from app.db.database import get_db

    db: Session = next(get_db())
    try:
        # Get list of tables (excluding SQLite system tables)
        tables_query = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"))
        table_names = [row[0] for row in tables_query.fetchall()]

        tables_info = []
        for table_name in table_names:
            # Get row count
            count_query = db.execute(text(f'SELECT COUNT(*) as count FROM "{table_name}";'))
            count = count_query.scalar() or 0

            # Get column info using PRAGMA
            pragma_query = db.execute(text(f'PRAGMA table_info("{table_name}");'))
            columns = []
            for col in pragma_query.fetchall():
                # col: (cid, name, type, notnull, dflt_value, pk)
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'pk': bool(col[5]),
                    'notnull': bool(col[3])
                })

            tables_info.append({
                'name': table_name,
                'count': count,
                'columns': columns
            })

        return templates.TemplateResponse(request, "database.html", {
            "tables_info": tables_info
        })
    finally:
        db.close()


@app.get("/leaderboard", include_in_schema=False)
async def leaderboard_page(request: Request):
    """Таблица лидеров раздел."""
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Get leaderboard data from service
        leaderboard_data = LeaderboardService.get_leaderboard(limit=10, db=db)
        return templates.TemplateResponse(request, "leaderboard.html", {
            "leaderboard": leaderboard_data
        })
    finally:
        db.close()


@app.get("/about", include_in_schema=False)
async def about_page(request: Request):
    """О проекте раздел."""
    return templates.TemplateResponse(request, "about.html", {})


@app.get("/feedback", include_in_schema=False)
async def feedback_page(request: Request):
    """Обратная связь раздел."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import Feedback
    from sqlalchemy import func

    db: Session = next(get_db())
    try:
        # Get feedback count and average rating
        feedback_count = db.query(Feedback).count()
        avg_rating_result = db.query(func.avg(Feedback.rating)).scalar()
        avg_rating = round(float(avg_rating_result), 1) if avg_rating_result else 0

        return templates.TemplateResponse(request, "feedback.html", {
            "feedback_count": feedback_count,
            "total_feedback": feedback_count,
            "avg_rating": avg_rating
        })
    finally:
        db.close()


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """Страница входа."""
    return templates.TemplateResponse(request, "login.html", {})


@app.get("/", include_in_schema=False)
async def home(request: Request):
    """Главная страница."""
    from sqlalchemy.orm import Session
    from app.db.database import get_db
    from app.db.models import Category, Topic, Question, GlossaryTerm

    # Получаем статистику
    db = next(get_db())
    try:
        stats = {
            "categories": db.query(Category).count(),
            "topics": db.query(Topic).count(),
            "questions": db.query(Question).count(),
            "glossary": db.query(GlossaryTerm).count()
        }
    finally:
        db.close()

    return templates.TemplateResponse(request, "index.html", {"stats": stats})
