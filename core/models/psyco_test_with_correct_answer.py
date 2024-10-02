# core/models/psyco_test_with_correct_answer.py

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Integer, String, ForeignKey
from typing import List

from .base import Base


class PycoTestWithCorrectAnswer(Base):
    """
    Представляет психологический тест с правильными ответами.
    Каждый вопрос имеет один правильный ответ.
    """
    __tablename__ = "pyco_tests_with_correct_answer"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    questions: Mapped[List["PsycoQuestionWithCorrectAnswer"]] = relationship(back_populates="test", cascade="all, delete-orphan")
    results: Mapped[List["PsycoResultWithFromToGroup"]] = relationship(back_populates="test", cascade="all, delete-orphan")

    def calculate_score(self, selected_answers: List["PsycoAnswerWithCorrectMarker"]) -> int:
        """
        Вычисляет количество правильных ответов.
        
        :param selected_answers: Список выбранных ответов
        :return: Количество правильных ответов
        """
        return sum(1 for answer in selected_answers if answer.is_correct)


class PsycoQuestionWithCorrectAnswer(Base):
    """
    Представляет вопрос в психологическом тесте с правильным ответом.
    """
    __tablename__ = "psyco_questions_with_correct_answer"

    question_text: Mapped[str] = mapped_column(String, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("pyco_tests_with_correct_answer.id"))

    test: Mapped[PycoTestWithCorrectAnswer] = relationship(back_populates="questions")
    answers: Mapped[List["PsycoAnswerWithCorrectMarker"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class PsycoAnswerWithCorrectMarker(Base):
    """
    Представляет вариант ответа на вопрос с маркером правильности.
    """
    __tablename__ = "psyco_answers_with_correct_marker"

    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("psyco_questions_with_correct_answer.id"))

    question: Mapped[PsycoQuestionWithCorrectAnswer] = relationship(back_populates="answers")


class PsycoResultWithFromToGroup(Base):
    """
    Представляет группу результатов теста на основе диапазона правильных ответов.
    """
    __tablename__ = "psyco_results_with_from_to_group"

    test_id: Mapped[int] = mapped_column(ForeignKey("pyco_tests_with_correct_answer.id"))
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    test: Mapped[PycoTestWithCorrectAnswer] = relationship(back_populates="results")
