# core/models/psyco_tests_with_score_answers.py

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from typing import List

from .base import Base


class PsycoTestWithScoreAnswers(Base):
    """
    Представляет психологический тест с системой подсчета очков.
    Каждый ответ на вопрос имеет определенное количество очков.
    """
    __tablename__ = "psyco_tests_with_score_answers"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    questions: Mapped[List["PsycoQuestionWithScoreAnswers"]] = relationship(back_populates="test", cascade="all, delete-orphan")
    results: Mapped[List["PsycoResultWithScoreGroup"]] = relationship(back_populates="test", cascade="all, delete-orphan")

    def calculate_total_score(self, selected_answers: List["PsycoAnswerWithScoreMarker"]) -> int:
        """
        Вычисляет общее количество очков на основе выбранных ответов.
        
        :param selected_answers: Список выбранных ответов
        :return: Общее количество очков
        """
        return sum(answer.score_value for answer in selected_answers)


class PsycoQuestionWithScoreAnswers(Base):
    """
    Представляет вопрос в психологическом тесте с системой подсчета очков.
    """
    __tablename__ = "psyco_questions_with_score_answers"

    question_text: Mapped[str] = mapped_column(String, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("psyco_tests_with_score_answers.id"))

    test: Mapped[PsycoTestWithScoreAnswers] = relationship(back_populates="questions")
    answers: Mapped[List["PsycoAnswerWithScoreMarker"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class PsycoAnswerWithScoreMarker(Base):
    """
    Представляет вариант ответа на вопрос с соответствующим количеством очков.
    """
    __tablename__ = "psyco_answers_with_score_marker"

    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    score_value: Mapped[int] = mapped_column(Integer, nullable=False)

    question_id: Mapped[int] = mapped_column(ForeignKey("psyco_questions_with_score_answers.id"))

    question: Mapped[PsycoQuestionWithScoreAnswers] = relationship(back_populates="answers")


class PsycoResultWithScoreGroup(Base):
    """
    Представляет группу результатов теста на основе диапазона очков.
    """
    __tablename__ = "psyco_results_with_score_group"

    test_id: Mapped[int] = mapped_column(ForeignKey("psyco_tests_with_score_answers.id"))
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    test: Mapped[PsycoTestWithScoreAnswers] = relationship(back_populates="results")
