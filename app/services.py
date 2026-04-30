"""
Сервисный слой для бизнес-логики образовательной платформы
"""
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models import (
    Achievement, DailyChallenge, SearchResults, CategoryStats,
    LeaderboardEntry, Certificate, Comment, Notification
)
from app.db.models import (
    Category, Topic, Quiz, Question, GlossaryTerm,
    UserProgress, QuizResult, ReadTopic
)


class ProgressService:
    """Сервис для управления прогрессом пользователя и геймификацией."""

    @staticmethod
    def calculate_level(experience: int) -> tuple:
        """Рассчитать уровень и опыт на основе общего опыта."""
        level = 1
        xp_required = 100
        total_xps = experience
        while total_xps >= xp_required:
            total_xps -= xp_required
            level += 1
            xp_required = int(xp_required * 1.5)
        return level, total_xps, xp_required

    @staticmethod
    def add_experience(session_id: str, amount: int, db: Session) -> None:
        """Добавить опыт пользователю."""
        progress = db.query(UserProgress).filter(
            UserProgress.session_id == session_id
        ).first()

        if progress:
            progress.total_score += amount
            progress.last_visit = datetime.now(UTC)
        else:
            user_progress = UserProgress(
                session_id=session_id,
                topics_read=0,
                quizzes_passed=0,
                total_score=amount,
                last_visit=datetime.now(UTC)
            )
            db.add(user_progress)
        db.commit()

    @staticmethod
    def get_achievements(session_id: str, db: Session) -> List[Achievement]:
        """Получить список достижений пользователя."""
        progress = db.query(UserProgress).filter(
            UserProgress.session_id == session_id
        ).first()

        if not progress:
            return []

        topics_read = progress.topics_read
        quizzes_passed = progress.quizzes_passed
        total_score = progress.total_score

        return [
            Achievement(
                id=1, name="Первые шаги",
                description="Прочитать первую тему",
                icon="📚", unlocked=topics_read >= 1
            ),
            Achievement(
                id=2, name="Любопытный",
                description="Прочитать 5 тем",
                icon="🔍", unlocked=topics_read >= 5
            ),
            Achievement(
                id=3, name="Эрудит",
                description="Прочитать 10 тем",
                icon="🎓", unlocked=topics_read >= 10
            ),
            Achievement(
                id=4, name="Новичок в тестировании",
                description="Пройти первый тест",
                icon="✅", unlocked=quizzes_passed >= 1
            ),
            Achievement(
                id=5, name="Опытный тестировщик",
                description="Пройти 5 тестов",
                icon="🏆", unlocked=quizzes_passed >= 5
            ),
            Achievement(
                id=6, name="Мастер тестирования",
                description="Набрать 100+ баллов в тестах",
                icon="👑", unlocked=total_score >= 100
            ),
        ]

    @staticmethod
    def get_daily_challenge(db: Session) -> Optional[DailyChallenge]:
        """Получить ежедневное испытание."""
        quiz = db.query(Quiz).order_by(func.random()).first()
        if not quiz:
            return None

        expires = datetime.now(UTC).replace(hour=23, minute=59, second=59)
        return DailyChallenge(
            id=1,
            quiz_id=quiz.id,
            title="Ежедневный вызов",
            description=f"Пройдите тест: {quiz.title} и получите 50 XP!",
            bonus_xp=50,
            completed=False,
            expires_at=expires.isoformat()
        )

    @staticmethod
    def get_category_stats(session_id: str, db: Session) -> List[CategoryStats]:
        """Получить статистику по категориям."""
        stats_query = db.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.count(Topic.id).label('total_topics'),
            func.count(ReadTopic.topic_id).label('read_topics'),
            func.count(Quiz.id).label('total_quizzes'),
            func.count(QuizResult.id).label('passed_quizzes'),
            func.coalesce(
                func.avg(QuizResult.score * 100.0 / QuizResult.total), 0
            ).label('average_score')
        ).outerjoin(
            Topic, Category.id == Topic.category_id
        ).outerjoin(
            ReadTopic,
            (Topic.id == ReadTopic.topic_id) & (ReadTopic.session_id == session_id)
        ).outerjoin(
            Quiz, Category.id == Quiz.category_id
        ).outerjoin(
            QuizResult, Quiz.id == QuizResult.quiz_id
        ).group_by(Category.id, Category.name).all()

        stats = []
        for row in stats_query:
            completion = 0.0
            if row.total_topics > 0:
                completion = (row.read_topics / row.total_topics) * 100
            stats.append(CategoryStats(
                category_id=row.category_id,
                category_name=row.category_name,
                total_topics=row.total_topics,
                read_topics=row.read_topics,
                total_quizzes=row.total_quizzes,
                passed_quizzes=row.passed_quizzes,
                average_score=row.average_score or 0.0,
                completion_percentage=completion
            ))
        return stats


class SearchService:
    """Сервис для поиска по материалам."""

    @staticmethod
    def search(query: str, db: Session) -> SearchResults:
        """Поиск по темам и глоссарию."""
        search_term = f"%{query}%"

        # Поиск по темам
        topics_query = db.query(Topic, Category.name.label('category_name'))\
            .join(Category, Topic.category_id == Category.id)\
            .filter(
                (Topic.title.ilike(search_term)) |
                (Topic.content.ilike(search_term))
            )\
            .limit(10)\
            .all()

        topics = [
            {
                "id": topic.id,
                "title": topic.title,
                "snippet": topic.content[:200] + "...",
                "category": category_name
            }
            for topic, category_name in topics_query
        ]

        # Поиск по глоссарию
        glossary_terms = db.query(GlossaryTerm).filter(
            (GlossaryTerm.term.ilike(search_term)) |
            (GlossaryTerm.definition.ilike(search_term))
        ).limit(10).all()

        glossary_results = [
            {
                "id": term.id,
                "term": term.term,
                "definition": term.definition
            }
            for term in glossary_terms
        ]

        return SearchResults(
            topics=topics,
            glossary_terms=glossary_results,
            query=query,
            total_results=len(topics) + len(glossary_results)
        )


class RecommendationService:
    """Сервис для рекомендаций контента."""

    @staticmethod
    def get_recommendations(session_id: str, limit: int = 3, db: Session = None) -> List[Dict[str, Any]]:
        """Получить рекомендации тем для изучения."""
        # Получить категории, которые пользователь ещё не изучал
        unread_categories = db.query(Category.id, Category.name).filter(
            Category.id.notin_(
                db.query(Topic.category_id).join(
                    ReadTopic, Topic.id == ReadTopic.topic_id
                ).filter(ReadTopic.session_id == session_id)
            )
        ).limit(limit).all()

        if not unread_categories:
            # Если все категории изучены, вернуть случайные темы
            recommendations = db.query(Topic, Category.name.label('category_name'))\
                .join(Category, Topic.category_id == Category.id)\
                .order_by(func.random())\
                .limit(limit)\
                .all()
            return [
                {
                    "id": topic.id,
                    "category_id": topic.category_id,
                    "title": topic.title,
                    "content": topic.content,
                    "order_num": topic.order_num,
                    "category_name": category_name
                }
                for topic, category_name in recommendations
            ]
        else:
            # Вернуть темы из непрочитанных категорий
            category_ids = [cat.id for cat in unread_categories]
            recommendations = db.query(Topic, Category.name.label('category_name'))\
                .join(Category, Topic.category_id == Category.id)\
                .filter(
                    Topic.category_id.in_(category_ids),
                    Topic.id.notin_(
                        db.query(ReadTopic.topic_id).filter(
                            ReadTopic.session_id == session_id
                        )
                    )
                )\
                .order_by(Topic.order_num)\
                .limit(limit)\
                .all()
            return [
                {
                    "id": topic.id,
                    "category_id": topic.category_id,
                    "title": topic.title,
                    "content": topic.content,
                    "order_num": topic.order_num,
                    "category_name": category_name
                }
                for topic, category_name in recommendations
            ]


class LeaderboardService:
    """Сервис для управления таблицей лидеров."""

    @staticmethod
    def get_leaderboard(limit: int = 10, db: Session = None) -> List[LeaderboardEntry]:
        """Получить таблицу лидеров."""
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


class CommentService:
    """Сервис для управления комментариями к темам."""

    @staticmethod
    def add_comment(topic_id: int, user_id: str, content: str, db: Session) -> Comment:
        """Добавить комментарий к теме."""
        from app.db.models import Comment

        comment = Comment(
            topic_id=topic_id,
            user_id=user_id,
            content=content,
            created_at=datetime.now(UTC),
            likes=0
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        return Comment(
            id=comment.id,
            topic_id=comment.topic_id,
            user_id=comment.user_id,
            username=f"User_{user_id[:8]}",
            content=comment.content,
            created_at=comment.created_at.isoformat(),
            likes=comment.likes
        )

    @staticmethod
    def get_comments(topic_id: int, db: Session) -> List[Comment]:
        """Получить комментарии к теме."""
        from app.db.models import Comment

        comments = db.query(Comment).filter(
            Comment.topic_id == topic_id
        ).order_by(Comment.created_at.desc()).all()

        return [
            Comment(
                id=c.id,
                topic_id=c.topic_id,
                user_id=c.user_id,
                username=f"User_{c.user_id[:8]}",
                content=c.content,
                created_at=c.created_at.isoformat(),
                likes=c.likes
            )
            for c in comments
        ]

    @staticmethod
    def like_comment(comment_id: str, db: Session) -> bool:
        """Поставить лайк комментарию."""
        from app.db.models import Comment

        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return False

        comment.likes += 1
        db.commit()
        return True


class NotificationService:
    """Сервис для управления уведомлениями."""

    @staticmethod
    def create_notification(
        user_id: str, title: str, message: str,
        notification_type: str, db: Session
    ) -> Notification:
        """Создать уведомление."""
        from app.db.models import Notification

        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            is_read=False,
            created_at=datetime.now(UTC)
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        return Notification(
            id=notif.id,
            user_id=notif.user_id,
            title=notif.title,
            message=notif.message,
            type=notif.type,
            is_read=notif.is_read,
            created_at=notif.created_at.isoformat()
        )

    @staticmethod
    def get_unread_notifications(user_id: str, db: Session) -> List[Notification]:
        """Получить непрочитанные уведомления."""
        from app.db.models import Notification

        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        ).order_by(Notification.created_at.desc()).all()

        return [
            Notification(
                id=n.id,
                user_id=n.user_id,
                title=n.title,
                message=n.message,
                type=n.type,
                is_read=n.is_read,
                created_at=n.created_at.isoformat()
            )
            for n in notifications
        ]

    @staticmethod
    def mark_as_read(notification_id: str, db: Session) -> bool:
        """Отметить уведомление как прочитанное."""
        from app.db.models import Notification

        notif = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notif:
            return False

        notif.is_read = True
        db.commit()
        return True


def seed_initial_data():
    """Заполнение БД начальными данными через SQLAlchemy."""
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        if db.query(Category).count() > 0:
            return

        # --- Категории ---
        categories_data = [
            Category(
                name="Функциональное тестирование",
                slug="functional",
                description="Проверка функциональности приложения согласно требованиям",
                icon="check-circle"
            ),
            Category(
                name="Нефункциональное тестирование",
                slug="non-functional",
                description="Тестирование производительности, безопасности и удобства",
                icon="shield"
            ),
            Category(
                name="Методологии тестирования",
                slug="methodologies",
                description="Подходы к организации процесса тестирования",
                icon="layers"
            ),
            Category(
                name="Инструменты тестирования",
                slug="tools",
                description="Обзор популярных инструментов и фреймворков",
                icon="wrench"
            ),
            Category(
                name="Процесс создания тестов",
                slug="test-creation",
                description="Разработка тест-кейсов, сценариев и чек-листов",
                icon="file-text"
            ),
        ]

        for cat in categories_data:
            db.add(cat)
        db.commit()

        # Получаем созданные категории
        categories = db.query(Category).all()
        cat_by_slug = {cat.slug: cat for cat in categories}

        # --- Темы ---
        topics_data = [
            (
                "functional",
                "Что такое функциональное тестирование",
                "Функциональное тестирование — это вид тестирования программного обеспечения, "
                "при котором проверяется соответствие системы функциональным требованиям."
            ),
            (
                "functional",
                "Чёрный и белый ящики: подходы к тестированию",
                "Существует два основных подхода к проектированию тестов: чёрный и белый ящик."
            ),
            (
                "non-functional",
                "Тестирование производительности",
                "Тестирование производительности оценивает скорость отклика и потребление ресурсов."
            ),
            (
                "non-functional",
                "Тестирование безопасности",
                "Тестирование безопасности направлено на выявление уязвимостей в системе."
            ),
            (
                "methodologies",
                "TDD: Разработка через тестирование",
                "TDD — методология, при которой тесты пишутся до написания кода."
            ),
            (
                "methodologies",
                "BDD: Поведенческая разработка",
                "BDD описывает поведение системы на естественном языке."
            ),
            (
                "tools",
                "Selenium для автоматизации",
                "Selenium — популярный инструмент для автоматизации веб-приложений."
            ),
            (
                "tools",
                "Postman для тестирования API",
                "Postman позволяет тестировать REST API и создавать коллекции запросов."
            ),
            (
                "test-creation",
                "Написание тест-кейсов",
                "Тест-кейс — документ, описывающий шаги для проверки функциональности."
            ),
            (
                "test-creation",
                "Чек-листы в тестировании",
                "Чек-лист — список проверок для быстрого тестирования."
            ),
        ]

        for idx, (slug, title, content) in enumerate(topics_data):
            category = cat_by_slug.get(slug)
            if category:
                topic = Topic(
                    category_id=category.id,
                    title=title,
                    content=content,
                    order_num=idx + 1
                )
                db.add(topic)

        # --- Тесты и вопросы ---
        quiz = Quiz(
            category_id=cat_by_slug["functional"].id,
            title="Основы функционального тестирования",
            description="Проверьте свои знания"
        )
        db.add(quiz)
        db.commit()

        questions_data = [
            (
                "Что проверяет функциональное тестирование?",
                "Соответствие требованиям", "Производительность",
                "Безопасность", "Удобство", "A",
                "Функциональное тестирование проверяет соответствие ПО функциональным требованиям."
            ),
            (
                "Какой подход использует знание внутреннего устройства кода?",
                "Чёрный ящик", "Белый ящик", "Серый ящик", "Зелёный ящик", "B",
                "Белый ящик предполагает знание внутренней структуры кода."
            ),
        ]

        for q_text, opt_a, opt_b, opt_c, opt_d, correct, explanation in questions_data:
            question = Question(
                quiz_id=quiz.id,
                question_text=q_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option=correct,
                explanation=explanation,
                order_num=1
            )
            db.add(question)

        # --- Глоссарий ---
        glossary_data = [
            ("Баг", "Ошибка в программном обеспечении", "Б"),
            ("Тест-кейс", "Документ с шагами для проверки функциональности", "Т"),
            ("Регрессионное тестирование", "Повторное тестирование после изменений", "Р"),
            ("Смоук-тестирование", "Быстрая проверка основной функциональности", "С"),
        ]

        for term, definition, letter in glossary_data:
            db.add(GlossaryTerm(term=term, definition=definition, letter=letter))

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
