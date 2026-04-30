"""
Сервис для социальных функций: комментарии и уведомления
"""
from datetime import datetime, UTC
from typing import List
from sqlalchemy.orm import Session

from app.models import Comment, Notification


class CommentService:
    """Сервис для управления комментариями к темам."""

    @staticmethod
    def add_comment(topic_id: int, user_id: str, content: str, db: Session) -> Comment:
        """Добавить комментарий к теме."""
        from app.db.models import Comment as CommentModel

        comment = CommentModel(
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
        from app.db.models import Comment as CommentModel

        comments = db.query(CommentModel).filter(
            CommentModel.topic_id == topic_id
        ).order_by(CommentModel.created_at.desc()).all()

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
        user_id: str, title: str, message: str,
        notification_type: str, db: Session
    ) -> Notification:
        """Создать уведомление."""
        from app.db.models import Notification as NotificationModel

        notif = NotificationModel(
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
        from app.db.models import Notification as NotificationModel

        notifications = db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read.is_(False)
        ).order_by(NotificationModel.created_at.desc()).all()

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
        from app.db.models import Notification as NotificationModel

        notif = db.query(NotificationModel).filter(
            NotificationModel.id == notification_id
        ).first()

        if not notif:
            return False

        notif.is_read = True
        db.commit()
        return True
