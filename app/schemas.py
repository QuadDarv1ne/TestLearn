"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""
    icon: str = "check-circle"


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    topics_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Topic schemas
class TopicBase(BaseModel):
    title: str
    content: str
    category_id: int
    order_num: int = 0


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int
    category_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Quiz schemas
class QuizBase(BaseModel):
    title: str
    description: str = ""
    category_id: Optional[int] = None


class QuizCreate(QuizBase):
    pass


class QuizResponse(QuizBase):
    id: int
    questions_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: str = ""
    quiz_id: int
    order_num: int = 0


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Quiz Result schemas
class QuizResultCreate(BaseModel):
    quiz_id: int
    score: int
    total: int


class QuizResultResponse(QuizResultCreate):
    id: str
    created_at: datetime
    percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


# Glossary schemas
class GlossaryTermBase(BaseModel):
    term: str
    definition: str
    letter: str


class GlossaryTermCreate(GlossaryTermBase):
    pass


class GlossaryTermResponse(GlossaryTermBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Feedback schemas
class FeedbackCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    message: str
    rating: int = 0


class FeedbackResponse(FeedbackCreate):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Progress schemas
class UserProgressBase(BaseModel):
    session_id: str
    topics_read: int = 0
    quizzes_passed: int = 0
    total_score: int = 0


class UserProgressResponse(UserProgressBase):
    id: str
    last_visit: datetime
    level: int = 1
    experience: int = 0

    model_config = ConfigDict(from_attributes=True)


# Authentication schemas
class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Comment schemas
class CommentCreate(BaseModel):
    topic_id: int
    content: str
    user_id: str


class CommentResponse(CommentCreate):
    id: str
    created_at: datetime
    likes: int = 0

    model_config = ConfigDict(from_attributes=True)


# Achievement schemas
class AchievementSchema(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Daily Challenge schemas
class DailyChallengeSchema(BaseModel):
    id: int
    quiz_id: int
    title: str
    description: str
    bonus_xp: int = 50
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


# Leaderboard entry
class LeaderboardEntry(BaseModel):
    session_id: str
    total_score: int
    rank: int

    model_config = ConfigDict(from_attributes=True)


# Certificate
class CertificateSchema(BaseModel):
    user_name: str
    course_name: str
    completion_date: str
    score: float

    model_config = ConfigDict(from_attributes=True)
