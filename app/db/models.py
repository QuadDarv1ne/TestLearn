"""
SQLAlchemy models for TestLearn application
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid
from app.db.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String, default="check-circle")

    topics = relationship("Topic", back_populates="category", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="category", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    order_num = Column(Integer, default=0)

    category = relationship("Category", back_populates="topics")
    comments = relationship("Comment", back_populates="topic", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="topic", cascade="all, delete-orphan")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")

    category = relationship("Category", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    results = relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)
    explanation = Column(String, default="")
    order_num = Column(Integer, default=0)

    quiz = relationship("Quiz", back_populates="questions")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    quiz = relationship("Quiz", back_populates="results")


class GlossaryTerm(Base):
    __tablename__ = "glossary"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, nullable=False)
    definition = Column(Text, nullable=False)
    letter = Column(String, nullable=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, default="")
    message = Column(Text, nullable=False)
    rating = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(UTC))


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, unique=True, nullable=False)
    topics_read = Column(Integer, default=0)
    quizzes_passed = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    last_visit = Column(DateTime, default=datetime.now(UTC))


class ReadTopic(Base):
    __tablename__ = "read_topics"

    session_id = Column(String, primary_key=True)
    topic_id = Column(Integer, primary_key=True)
    read_at = Column(DateTime, default=datetime.now(UTC))


class Bookmark(Base):
    __tablename__ = "bookmarks"

    session_id = Column(String, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), primary_key=True)
    bookmarked_at = Column(DateTime, default=datetime.now(UTC))

    topic = relationship("Topic", back_populates="bookmarks")


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    expires = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    user_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    likes = Column(Integer, default=0)

    topic = relationship("Topic", back_populates="comments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))


class AdminUser(Base):
    """Model for admin users with hashed passwords."""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    is_active = Column(Boolean, default=True)


class AchievementDefinition(Base):
    """Definition of available achievements in the system."""
    __tablename__ = "achievement_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)
    category = Column(String, default="general")  # general, quiz, topic, streak, social
    requirement_type = Column(String, nullable=False)  # count, percentage, special
    requirement_value = Column(Integer, default=0)
    xp_reward = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)


class UserAchievement(Base):
    """User's unlocked achievements."""
    __tablename__ = "user_achievements"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievement_definitions.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.now(UTC))
    notification_sent = Column(Boolean, default=False)

    achievement = relationship("AchievementDefinition", backref="user_achievements")
