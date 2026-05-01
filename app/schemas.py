"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import re

# Question types
QUESTION_TYPE_SINGLE_CHOICE = "single_choice"
QUESTION_TYPE_MULTIPLE_CHOICE = "multiple_choice"
QUESTION_TYPE_TRUE_FALSE = "true_false"
QUESTION_TYPE_SHORT_ANSWER = "short_answer"
QUESTION_TYPE_MATCHING = "matching"
QUESTION_TYPE_ORDERING = "ordering"
QUESTION_TYPE_FILL_BLANK = "fill_blank"

VALID_QUESTION_TYPES = [
    QUESTION_TYPE_SINGLE_CHOICE,
    QUESTION_TYPE_MULTIPLE_CHOICE,
    QUESTION_TYPE_TRUE_FALSE,
    QUESTION_TYPE_SHORT_ANSWER,
    QUESTION_TYPE_MATCHING,
    QUESTION_TYPE_ORDERING,
    QUESTION_TYPE_FILL_BLANK,
]

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
    question_type: str = QUESTION_TYPE_SINGLE_CHOICE
    quiz_id: int
    order_num: int = 0
    points: int = 1
    
    # For single_choice and multiple_choice questions
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[str] = None
    
    # For true_false questions
    is_true: Optional[bool] = None
    
    # For short_answer and fill_blank questions
    correct_answer: Optional[str] = None
    case_sensitive: bool = False
    
    # For matching questions
    matching_pairs: Optional[Dict[str, Any]] = None
    correct_matches: Optional[Dict[str, str]] = None
    
    # For ordering questions
    ordering_items: Optional[List[str]] = None
    correct_order: Optional[Union[List[int], List[str]]] = None
    
    # For fill_blank questions
    blank_positions: Optional[List[int]] = None
    
    explanation: str = ""

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Quiz Answer submission schema
class QuizAnswerSubmit(BaseModel):
    question_id: int
    answer: Any

class QuizSubmit(BaseModel):
    quiz_id: int
    answers: List[QuizAnswerSubmit]
    session_id: Optional[str] = None

# Quiz Result schemas
class QuizResultCreate(BaseModel):
    quiz_id: int
    score: int
    total: int
    total_points: int = 0
    answers: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class QuizResultResponse(QuizResultCreate):
    id: str
    created_at: str
    percentage: float = 0.0
    model_config = ConfigDict(from_attributes=True)

class QuizResultDetail(QuizResultResponse):
    question_results: List[Dict[str, Any]] = []

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
    rating: int = 5
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty and has reasonable length."""
        if not v or not v.strip():
            raise ValueError('Name is required')
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Name must be between 2 and 100 characters')
        return v
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty and has reasonable length."""
        if not v or not v.strip():
            raise ValueError('Message is required')
        v = v.strip()
        if len(v) < 5 or len(v) > 2000:
            raise ValueError('Message must be between 5 and 2000 characters')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format if provided."""
        if not v or v.strip() == "":
            return ""  # Email is optional, return empty string if not provided
        v = v.strip()
        # More strict email regex validation
        email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        if len(v) > 254:
            raise ValueError('Email is too long')
        return v
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating is between 1 and 5."""
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class FeedbackResponse(FeedbackCreate):
    id: str
    created_at: str
    model_config = ConfigDict(from_attributes=True)

# User Progress schemas
class UserProgressBase(BaseModel):
    session_id: str
    topics_read: int = 0
    quizzes_passed: int = 0
    total_score: int = 0

class UserProgressResponse(UserProgressBase):
    id: str
    last_visit: str
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
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content is not empty and has reasonable length."""
        if not v or not v.strip():
            raise ValueError('Comment content is required')
        v = v.strip()
        if len(v) < 3 or len(v) > 1000:
            raise ValueError('Comment must be between 3 and 1000 characters')
        return v

class CommentResponse(CommentCreate):
    id: str
    created_at: str
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

# Certificate class
class CertificateSchema(BaseModel):
    user_name: str
    course_name: str
    completion_date: str
    score: float
    model_config = ConfigDict(from_attributes=True)

# Notification schemas
class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str
    model_config = ConfigDict(from_attributes=True)
