"""
Модели данных для образовательной платформы TestLearn
"""
from pydantic import BaseModel
from typing import Optional, List


class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: str = "check-circle"
    topics_count: int = 0


class Topic(BaseModel):
    id: int
    category_id: int
    title: str
    content: str
    order_num: int = 0
    category_name: Optional[str] = None


class Quiz(BaseModel):
    id: int
    category_id: Optional[int] = None
    title: str
    description: str = ""
    questions_count: int = 0


class Question(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: str = ""
    order_num: int = 0


class QuizResult(BaseModel):
    id: str
    quiz_id: int
    score: int
    total: int
    created_at: str
    percentage: float = 0.0


class GlossaryTerm(BaseModel):
    id: int
    term: str
    definition: str
    letter: str


class Feedback(BaseModel):
    id: str
    name: str
    email: str = ""
    message: str
    rating: int = 0
    created_at: str


class UserProgress(BaseModel):
    id: str
    session_id: str
    topics_read: int = 0
    quizzes_passed: int = 0
    total_score: int = 0
    last_visit: str
    level: int = 1
    experience: int = 0
    next_level_xp: int = 100


class Achievement(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[str] = None


class DailyChallenge(BaseModel):
    id: int
    quiz_id: int
    title: str
    description: str
    bonus_xp: int = 50
    completed: bool = False
    expires_at: str


class SearchResults(BaseModel):
    topics: List[dict] = []
    glossary_terms: List[dict] = []
    query: str = ""
    total_results: int = 0


class CategoryStats(BaseModel):
    category_id: int
    category_name: str
    total_topics: int
    read_topics: int
    total_quizzes: int
    passed_quizzes: int
    average_score: float = 0.0
    completion_percentage: float = 0.0


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    level: int
    experience: int
    quizzes_passed: int
    average_score: float = 0.0


class Certificate(BaseModel):
    id: str
    user_id: str
    username: str
    issued_at: str
    level: int
    topics_completed: int
    quizzes_passed: int
    average_score: float
    certificate_url: str


class Comment(BaseModel):
    id: str
    topic_id: int
    user_id: str
    username: str
    content: str
    created_at: str
    likes: int = 0


class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str  # "new_topic", "achievement", "challenge"
    is_read: bool = False
    created_at: str
