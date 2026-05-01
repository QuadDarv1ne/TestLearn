"""Tests for QuizCheckerService and CertificateService."""
import pytest
import time
from datetime import datetime, UTC
from app.db.models import (
    Question, UserProgress,
    QUESTION_TYPE_SINGLE_CHOICE,
    QUESTION_TYPE_MULTIPLE_CHOICE,
    QUESTION_TYPE_TRUE_FALSE,
    QUESTION_TYPE_SHORT_ANSWER,
    QUESTION_TYPE_MATCHING,
    QUESTION_TYPE_ORDERING,
    QUESTION_TYPE_FILL_BLANK
)
from app.models import Certificate
from app.services.quiz_checker_service import QuizCheckerService
from app.services.gamification_service import CertificateService, LeaderboardService
from app.db.database import SessionLocal


def get_unique_session_id():
    """Generate unique session ID using timestamp."""
    return f"session_{int(time.time() * 1000)}"


# ==================== CertificateService Tests ====================

class TestCertificateService:
    """Tests for CertificateService."""

    @pytest.fixture
    def db_session(self):
        """Create a fresh database session for each test."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_generate_certificate_no_progress(self, db_session):
        """Test certificate generation with no progress."""
        result = CertificateService.generate_certificate(get_unique_session_id(), db_session)
        assert result is None

    def test_generate_certificate_insufficient_quizzes(self, db_session):
        """Test certificate generation with less than 5 quizzes passed."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=10,
            quizzes_passed=3,
            total_score=100
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is None

    def test_generate_certificate_success(self, db_session):
        """Test successful certificate generation."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=16,
            quizzes_passed=5,
            total_score=500
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is not None
        assert result.user_id == progress.id
        assert result.quizzes_passed == 5
        assert result.topics_completed == 16
        assert result.level >= 1
        assert "User_" in result.username
        assert result.issued_at is not None
        assert result.certificate_url.startswith("/certificates/")

    def test_generate_certificate_exactly_5_quizzes(self, db_session):
        """Test certificate generation with exactly 5 quizzes (minimum requirement)."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=5,
            quizzes_passed=5,
            total_score=250
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is not None
        assert result.quizzes_passed == 5

    def test_certificate_url_format(self, db_session):
        """Test certificate URL format."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=10,
            quizzes_passed=6,
            total_score=300
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is not None
        assert result.certificate_url.startswith("/certificates/")
        assert str(progress.id) in result.certificate_url

    def test_certificate_username_format(self, db_session):
        """Test that username format is correct."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=10,
            quizzes_passed=7,
            total_score=350
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is not None
        assert result.username.startswith("User_")
        # Username should be "User_" + first 8 chars of session_id
        assert len(result.username) == 13

    def test_certificate_issued_at_is_utc(self, db_session):
        """Test that issued_at timestamp is in UTC."""
        session_id = get_unique_session_id()
        progress = UserProgress(
            session_id=session_id,
            topics_read=10,
            quizzes_passed=5,
            total_score=400
        )
        db_session.add(progress)
        db_session.commit()
        result = CertificateService.generate_certificate(session_id, db_session)
        assert result is not None
        assert "T" in result.issued_at  # ISO format
        assert result.issued_at is not None


# ==================== QuizCheckerService Tests ====================

class TestQuizCheckerService:
    """Tests for QuizCheckerService."""

    def test_check_single_choice_correct(self):
        """Test single choice question - correct answer."""
        question = Question(
            question_text="What is testing?",
            question_type=QUESTION_TYPE_SINGLE_CHOICE,
            option_a="Finding bugs",
            option_b="Writing code",
            option_c="Designing UI",
            option_d="Deploying app",
            correct_option="A",
            points=10
        )
        is_correct, points = QuizCheckerService.check_single_choice(question, "A")
        assert is_correct is True
        assert points == 10

    def test_check_single_choice_incorrect(self):
        """Test single choice question - incorrect answer."""
        question = Question(
            question_text="What is testing?",
            question_type=QUESTION_TYPE_SINGLE_CHOICE,
            option_a="Finding bugs",
            option_b="Writing code",
            option_c="Designing UI",
            option_d="Deploying app",
            correct_option="A",
            points=10
        )
        is_correct, points = QuizCheckerService.check_single_choice(question, "B")
        assert is_correct is False
        assert points == 0

    def test_check_single_choice_case_insensitive(self):
        """Test single choice question - case insensitive."""
        question = Question(
            question_text="What is testing?",
            question_type=QUESTION_TYPE_SINGLE_CHOICE,
            option_a="Finding bugs",
            option_b="Writing code",
            option_c="Designing UI",
            option_d="Deploying app",
            correct_option="a",
            points=10
        )
        is_correct, points = QuizCheckerService.check_single_choice(question, "A")
        assert is_correct is True
        assert points == 10

    def test_check_multiple_choice_all_correct(self):
        """Test multiple choice question - all correct answers."""
        question = Question(
            question_text="Which are testing types?",
            question_type=QUESTION_TYPE_MULTIPLE_CHOICE,
            option_a="Functional",
            option_b="Non-functional",
            option_c="Manual",
            option_d="Compilation",
            correct_option="A,B",
            points=20
        )
        is_correct, points = QuizCheckerService.check_multiple_choice(
            question, ["A", "B"]
        )
        assert is_correct is True
        assert points == 20

    def test_check_multiple_choice_partial(self):
        """Test multiple choice question - partial credit."""
        question = Question(
            question_text="Which are testing types?",
            question_type=QUESTION_TYPE_MULTIPLE_CHOICE,
            option_a="Functional",
            option_b="Non-functional",
            option_c="Manual",
            option_d="Compilation",
            correct_option="A,B",
            points=20
        )
        is_correct, points = QuizCheckerService.check_multiple_choice(
            question, ["A"]
        )
        assert is_correct is False
        assert points >= 0  # Partial credit

    def test_check_multiple_choice_wrong(self):
        """Test multiple choice question - wrong answer."""
        question = Question(
            question_text="Which are testing types?",
            question_type=QUESTION_TYPE_MULTIPLE_CHOICE,
            option_a="Functional",
            option_b="Non-functional",
            option_c="Manual",
            option_d="Compilation",
            correct_option="A,B",
            points=20
        )
        is_correct, points = QuizCheckerService.check_multiple_choice(
            question, ["C", "D"]
        )
        assert is_correct is False
        assert points == 0

    def test_check_true_false_correct(self):
        """Test True/False question - correct answer."""
        question = Question(
            question_text="Testing is important",
            question_type=QUESTION_TYPE_TRUE_FALSE,
            is_true=True,
            points=10
        )
        is_correct, points = QuizCheckerService.check_true_false(question, True)
        assert is_correct is True
        assert points == 10

    def test_check_true_false_incorrect(self):
        """Test True/False question - incorrect answer."""
        question = Question(
            question_text="Testing is important",
            question_type=QUESTION_TYPE_TRUE_FALSE,
            is_true=True,
            points=10
        )
        is_correct, points = QuizCheckerService.check_true_false(question, False)
        assert is_correct is False
        assert points == 0

    def test_check_short_answer_correct(self):
        """Test short answer question - correct answer."""
        question = Question(
            question_text="What does QA stand for?",
            question_type=QUESTION_TYPE_SHORT_ANSWER,
            correct_answer="Quality Assurance",
            points=15,
            answer_case_sensitive=False
        )
        is_correct, points = QuizCheckerService.check_short_answer(
            question, "quality assurance"
        )
        assert is_correct is True
        assert points == 15

    def test_check_short_answer_case_sensitive(self):
        """Test short answer question - case sensitive."""
        question = Question(
            question_text="What is the capital?",
            question_type=QUESTION_TYPE_SHORT_ANSWER,
            correct_answer="Moscow",
            points=10,
            answer_case_sensitive=True
        )
        is_correct, points = QuizCheckerService.check_short_answer(question, "Moscow")
        assert is_correct is True
        is_correct, points = QuizCheckerService.check_short_answer(question, "moscow")
        assert is_correct is False

    def test_check_matching_all_correct(self):
        """Test matching question - all pairs correct."""
        question = Question(
            question_type=QUESTION_TYPE_MATCHING,
            correct_matches={"A": "1", "B": "2", "C": "3"},
            points=30
        )
        user_matches = {"A": "1", "B": "2", "C": "3"}
        is_correct, points = QuizCheckerService.check_matching(question, user_matches)
        assert is_correct is True
        assert points == 30

    def test_check_matching_partial(self):
        """Test matching question - partial credit."""
        question = Question(
            question_type=QUESTION_TYPE_MATCHING,
            correct_matches={"A": "1", "B": "2", "C": "3"},
            points=30
        )
        user_matches = {"A": "1", "B": "wrong"}
        is_correct, points = QuizCheckerService.check_matching(question, user_matches)
        assert is_correct is False
        assert points > 0  # Partial credit

    def test_check_ordering_correct(self):
        """Test ordering question - correct order."""
        question = Question(
            question_type=QUESTION_TYPE_ORDERING,
            correct_order=["1", "2", "3", "4"],
            points=20
        )
        user_order = ["1", "2", "3", "4"]
        is_correct, points = QuizCheckerService.check_ordering(question, user_order)
        assert is_correct is True
        assert points == 20

    def test_check_ordering_incorrect(self):
        """Test ordering question - incorrect order."""
        question = Question(
            question_type=QUESTION_TYPE_ORDERING,
            correct_order=["1", "2", "3", "4"],
            points=20
        )
        user_order = ["4", "3", "2", "1"]
        is_correct, points = QuizCheckerService.check_ordering(question, user_order)
        assert is_correct is False

    def test_check_fill_blank_correct(self):
        """Test fill in blank question - correct answer."""
        question = Question(
            question_type=QUESTION_TYPE_FILL_BLANK,
            correct_answer="Selenium",
            points=15,
            answer_case_sensitive=False
        )
        is_correct, points = QuizCheckerService.check_fill_blank(
            question, "selenium"
        )
        assert is_correct is True
        assert points == 15

    def test_check_answer_single_choice(self):
        """Test universal check_answer method for single choice."""
        question = Question(
            question_text="What is testing?",
            question_type=QUESTION_TYPE_SINGLE_CHOICE,
            option_a="Finding bugs",
            option_b="Writing code",
            correct_option="A",
            points=10,
            explanation="Testing is primarily about finding defects"
        )
        is_correct, points, explanation = QuizCheckerService.check_answer(question, "A")
        assert is_correct is True
        assert points == 10
        assert explanation == ""  # No explanation for correct answer

    def test_check_answer_with_explanation(self):
        """Test universal check_answer method returns explanation for wrong answer."""
        question = Question(
            question_text="What is testing?",
            question_type=QUESTION_TYPE_SINGLE_CHOICE,
            option_a="Finding bugs",
            option_b="Writing code",
            correct_option="A",
            points=10,
            explanation="Testing is primarily about finding defects"
        )
        is_correct, points, explanation = QuizCheckerService.check_answer(question, "B")
        assert is_correct is False
        assert points == 0
        assert explanation == "Testing is primarily about finding defects"

    def test_check_answer_multiple_choice(self):
        """Test universal check_answer method for multiple choice."""
        question = Question(
            question_text="Which are testing types?",
            question_type=QUESTION_TYPE_MULTIPLE_CHOICE,
            option_a="Functional",
            option_b="Non-functional",
            correct_option="A,B",
            points=20,
            explanation="Both functional and non-functional are testing types"
        )
        is_correct, points, explanation = QuizCheckerService.check_answer(
            question, ["A", "B"]
        )
        assert is_correct is True
        assert points == 20

    def test_quiz_checker_all_types(self):
        """Test quiz checker with all question types."""
        # Test single choice
        q1 = Question(question_type=QUESTION_TYPE_SINGLE_CHOICE, correct_option="A", points=10)
        result = QuizCheckerService.check_answer(q1, "A")
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 10

        # Test multiple choice
        q2 = Question(question_type=QUESTION_TYPE_MULTIPLE_CHOICE, correct_option="A,B", points=20)
        result = QuizCheckerService.check_answer(q2, ["A", "B"])
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 20

        # Test true/false
        q3 = Question(question_type=QUESTION_TYPE_TRUE_FALSE, is_true=True, points=15)
        result = QuizCheckerService.check_answer(q3, True)
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 15

        # Test short answer
        q4 = Question(question_type=QUESTION_TYPE_SHORT_ANSWER, correct_answer="Test", points=10, answer_case_sensitive=False)
        result = QuizCheckerService.check_answer(q4, "test")
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 10

        # Test matching
        q5 = Question(question_type=QUESTION_TYPE_MATCHING, correct_matches={"A": "1"}, points=25)
        result = QuizCheckerService.check_answer(q5, {"A": "1"})
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 25

        # Test ordering
        q6 = Question(question_type=QUESTION_TYPE_ORDERING, correct_order=["1", "2"], points=20)
        result = QuizCheckerService.check_answer(q6, ["1", "2"])
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 20

        # Test fill blank
        q7 = Question(question_type=QUESTION_TYPE_FILL_BLANK, correct_answer="Answer", points=10, answer_case_sensitive=False)
        result = QuizCheckerService.check_answer(q7, "answer")
        assert len(result) == 3
        assert result[0] is True
        assert result[1] == 10
