"""
Сервис для проверки ответов на вопросы различных типов.
Поддерживает: single_choice, multiple_choice, true_false, short_answer, matching, ordering, fill_blank.
"""
from typing import List, Dict, Any, Tuple

from app.db.models import Question
from app.db.models import (
    QUESTION_TYPE_SINGLE_CHOICE, QUESTION_TYPE_MULTIPLE_CHOICE,
    QUESTION_TYPE_TRUE_FALSE, QUESTION_TYPE_SHORT_ANSWER,
    QUESTION_TYPE_MATCHING, QUESTION_TYPE_ORDERING, QUESTION_TYPE_FILL_BLANK
)


class QuizCheckerService:
    """Сервис для проверки ответов на вопросы различных типов."""

    @staticmethod
    def check_single_choice(question: Question, user_answer: str) -> Tuple[bool, int]:
        """Проверка вопроса с одним правильным ответом."""
        is_correct = user_answer.upper() == question.correct_option.upper()
        points = question.points if is_correct else 0
        return is_correct, points

    @staticmethod
    def check_multiple_choice(question: Question, user_answers: List[str]) -> Tuple[bool, int]:
        """Проверка вопроса с несколькими правильными ответами."""
        if not question.correct_option:
            return False, 0
        
        # Parse correct answers (e.g., "A,B,C")
        correct_answers = set(ans.strip().upper() for ans in question.correct_option.split(','))
        user_answers_set = set(ans.strip().upper() for ans in user_answers)
        
        if not correct_answers:
            return False, 0
        
        correct_count = len(correct_answers & user_answers_set)
        incorrect_count = len(user_answers_set - correct_answers)
        
        # Full points only if all correct and no extra
        if user_answers_set == correct_answers:
            return True, question.points
        
        # Partial credit: reduce points for wrong/missed answers
        partial_ratio = max(0, (correct_count - incorrect_count) / len(correct_answers))
        points = int(question.points * partial_ratio)
        
        return user_answers_set == correct_answers, points

    @staticmethod
    def check_true_false(question: Question, user_answer: bool) -> Tuple[bool, int]:
        """Проверка вопроса True/False."""
        is_correct = (user_answer == question.is_true)
        points = question.points if is_correct else 0
        return is_correct, points

    @staticmethod
    def check_short_answer(question: Question, user_answer: str) -> Tuple[bool, int]:
        """Проверка вопроса с коротким текстовым ответом."""
        if not question.correct_answer:
            return False, 0
        
        expected = question.correct_answer.strip()
        user = user_answer.strip()
        
        if question.answer_case_sensitive:
            is_correct = user == expected
        else:
            is_correct = user.lower() == expected.lower()
        
        points = question.points if is_correct else 0
        return is_correct, points

    @staticmethod
    def check_matching(question: Question, user_matches: Dict[str, str]) -> Tuple[bool, int]:
        """Проверка вопроса на сопоставление пар."""
        if not question.correct_matches:
            return False, 0
        
        correct = question.correct_matches
        total_pairs = len(correct)
        
        if total_pairs == 0:
            return False, 0
        
        correct_count = sum(1 for k, v in user_matches.items() if correct.get(k) == v)
        
        if correct_count == total_pairs:
            return True, question.points
        
        # Partial credit based on correctly matched pairs
        points = int(question.points * correct_count / total_pairs)
        return correct_count == total_pairs, points

    @staticmethod
    def check_ordering(question: Question, user_order: List[Any]) -> Tuple[bool, int]:
        """Проверка вопроса на упорядочивание."""
        if not question.correct_order:
            return False, 0
        
        correct = question.correct_order
        
        # Normalize both to same type for comparison
        if isinstance(correct[0], int):
            user_normalized = [int(x) for x in user_order]
        else:
            user_normalized = [str(x) for x in user_order]
            correct = [str(x) for x in correct]
        
        if user_normalized == correct:
            return True, question.points
        
        # Calculate similarity for partial credit
        correct_positions = sum(1 for i, v in enumerate(user_normalized) if i < len(correct) and v == correct[i])
        partial_ratio = correct_positions / len(correct) if correct else 0
        points = int(question.points * partial_ratio)
        
        return user_normalized == correct, points

    @staticmethod
    def check_fill_blank(question: Question, user_answer: str) -> Tuple[bool, int]:
        """Проверка вопроса с заполнением пропусков."""
        if not question.correct_answer:
            return False, 0
        
        expected = question.correct_answer.strip()
        user = user_answer.strip()
        
        if question.answer_case_sensitive:
            is_correct = user == expected
        else:
            is_correct = user.lower() == expected.lower()
        
        points = question.points if is_correct else 0
        return is_correct, points

    @staticmethod
    def check_answer(question: Question, user_answer: Any) -> Tuple[bool, int, str]:
        """Универсальный метод проверки ответа на вопрос любого типа."""
        q_type = question.question_type or QUESTION_TYPE_SINGLE_CHOICE
        
        if q_type == QUESTION_TYPE_SINGLE_CHOICE:
            is_correct, points = QuizCheckerService.check_single_choice(question, str(user_answer))
        elif q_type == QUESTION_TYPE_MULTIPLE_CHOICE:
            is_correct, points = QuizCheckerService.check_multiple_choice(question, user_answer)
        elif q_type == QUESTION_TYPE_TRUE_FALSE:
            is_correct, points = QuizCheckerService.check_true_false(question, bool(user_answer))
        elif q_type == QUESTION_TYPE_SHORT_ANSWER:
            is_correct, points = QuizCheckerService.check_short_answer(question, str(user_answer))
        elif q_type == QUESTION_TYPE_MATCHING:
            is_correct, points = QuizCheckerService.check_matching(question, user_answer)
        elif q_type == QUESTION_TYPE_ORDERING:
            is_correct, points = QuizCheckerService.check_ordering(question, user_answer)
        elif q_type == QUESTION_TYPE_FILL_BLANK:
            is_correct, points = QuizCheckerService.check_fill_blank(question, str(user_answer))
        else:
            is_correct, points = False, 0
        
        explanation = question.explanation if not is_correct else ""
        return is_correct, points, explanation
