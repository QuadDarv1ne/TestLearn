"""Сервис для социальных функций: комментарии и уведомления."""
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy.orm import Session

class CommentService:
    """Сервис для управления комментариями к темам."""
    
    @staticmethod
    def add_comment(topic_id: int, user_id: str, content: str, db: Session) -> Optional["Comment"]:
        """Добавить комментарий к теме."""
        from app.db.models import Comment as CommentModel, Topic
        
        # Валидация контента
        if not content or not content.strip():
            return None
        if len(content.strip()) < 3:
            return None
        if len(content) > 1000:
            return None
        
        # Проверка существования темы
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return None
        
        comment = CommentModel(
            topic_id=topic_id,
            user_id=user_id,
            content=content.strip(),
            created_at=datetime.now(UTC),
            likes=0
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        from app.schemas import CommentResponse
        return CommentResponse(
            id=comment.id,
            topic_id=comment.topic_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=comment.created_at.isoformat(),
            likes=comment.likes
        )
    
    @staticmethod
    def get_comments(topic_id: int, db: Session, limit: int = 20, offset: int = 0) -> dict:
        """
        Получить комментарии к теме с пагинацией.
        
        Args:
            topic_id: ID темы
            db: Сессия базы данных
            limit: Максимальное количество записей (по умолчанию 20)
            offset: Смещение для пагинации (по умолчанию 0)
            
        Returns:
            Словарь с комментариями и метаданными пагинации
        """
        from app.db.models import Comment as CommentModel
        from app.schemas import CommentResponse
        
        # Валидация параметров
        if limit is None or limit < 1:
            limit = 20
        if limit > 100:
            limit = 100
        if offset is None or offset < 0:
            offset = 0
        
        # Получаем общее количество комментариев
        total = db.query(CommentModel).filter(CommentModel.topic_id == topic_id).count()
        
        # Получаем комментарии для текущей страницы
        comments = db.query(CommentModel).filter(
            CommentModel.topic_id == topic_id
        ).order_by(
            CommentModel.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Конвертируем в Response
        items = [
            CommentResponse(
                id=c.id,
                topic_id=c.topic_id,
                user_id=c.user_id,
                content=c.content,
                created_at=c.created_at.isoformat(),
                likes=c.likes
            )
            for c in comments
        ]
        
        # Рассчитываем метаданные пагинации
        page_size = limit
        page = (offset // page_size) + 1 if page_size > 0 else 1
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": offset + len(items) < total,
            "has_prev": offset > 0
        }
    
    @staticmethod
    def like_comment(comment_id: str, db: Session) -> bool:
        """Поставить лайк комментарию."""
        from app.db.models import Comment as CommentModel
        comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
        if not comment:
            return False
        comment.likes += 1
        db.commit()
        return True

class NotificationService:
    """Сервис для управления уведомлениями."""
    
    @staticmethod
    def create_notification(
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        db: Session
    ) -> Optional["Notification"]:
        """Создать уведомление."""
        from app.db.models import Notification as NotificationModel
        
        # Валидация
        if not title or not title.strip():
            return None
        if not message or not message.strip():
            return None
        
        notif = NotificationModel(
            user_id=user_id,
            title=title.strip(),
            message=message.strip(),
            type=notification_type,
            is_read=False,
            created_at=datetime.now(UTC)
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        
        from app.schemas import NotificationResponse
        return NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            title=notif.title,
            message=notif.message,
            type=notif.type,
            is_read=notif.is_read,
            created_at=notif.created_at.isoformat()
        )
    
    @staticmethod
    def get_unread_notifications(user_id: str, db: Session, limit: int = 20, offset: int = 0) -> dict:
        """
        Получить непрочитанные уведомления с пагинацией.
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            limit: Максимальное количество записей (по умолчанию 20)
            offset: Смещение для пагинации (по умолчанию 0)
            
        Returns:
            Словарь с уведомлениями и метаданными пагинации
        """
        from app.db.models import Notification as NotificationModel
        from app.schemas import NotificationResponse
        
        # Валидация параметров
        if limit is None or limit < 1:
            limit = 20
        if limit > 100:
            limit = 100
        if offset is None or offset < 0:
            offset = 0
        
        # Получаем общее количество непрочитанных уведомлений
        total = db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read.is_(False)
        ).count()
        
        # Получаем уведомления для текущей страницы
        notifications = db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read.is_(False)
        ).order_by(
            NotificationModel.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Конвертируем в Response
        items = [
            NotificationResponse(
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
        
        # Рассчитываем метаданные пагинации
        page_size = limit
        page = (offset // page_size) + 1 if page_size > 0 else 1
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": offset + len(items) < total,
            "has_prev": offset > 0
        }
    
    @staticmethod
    def mark_as_read(notification_id: str, db: Session) -> bool:
        """Отметить уведомление как прочитанное."""
        from app.db.models import Notification as NotificationModel
        notif = db.query(NotificationModel).filter(
            NotificationModel.id == notification_id
        ).first()
        if not notif:
            return False
        notif.is_read = True
        db.commit()
        return True
