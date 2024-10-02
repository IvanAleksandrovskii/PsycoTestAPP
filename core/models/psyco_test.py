# core/models/psyco_test.py

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Integer, String, ForeignKey
from typing import List, Optional

from .base import Base

class PsycoAnswer(Base):
    """
    Represents a generic answer that can be used across different question types.
    """
    __tablename__ = "psyco_answers"

    answer_text: Mapped[str] = mapped_column(String, nullable=False)

class PsycoTest(Base):
    """
    Represents a generic psychological test.
    """
    __tablename__ = "psyco_tests"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    test_type: Mapped[str] = mapped_column(String, nullable=False)

    questions: Mapped[List["PsycoQuestion"]] = relationship(back_populates="test", cascade="all, delete-orphan")
    results: Mapped[List["PsycoResult"]] = relationship(back_populates="test", cascade="all, delete-orphan")

class PsycoQuestion(Base):
    """
    Represents a question in a psychological test.
    """
    __tablename__ = "psyco_questions"

    question_text: Mapped[str] = mapped_column(String, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("psyco_tests.id"))

    test: Mapped[PsycoTest] = relationship(back_populates="questions")
    answer_options: Mapped[List["PsycoQuestionAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan")

class PsycoQuestionAnswer(Base):
    """
    Represents the association between a question and an answer, including metadata specific to the question-answer pair.
    """
    __tablename__ = "psyco_question_answers"

    question_id: Mapped[int] = mapped_column(ForeignKey("psyco_questions.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("psyco_answers.id"))
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    score_value: Mapped[Optional[int]] = mapped_column(Integer)

    question: Mapped[PsycoQuestion] = relationship(back_populates="answer_options")
    answer: Mapped[PsycoAnswer] = relationship()

class PsycoResult(Base):
    """
    Represents a result group for a psychological test.
    """
    __tablename__ = "psyco_results"

    test_id: Mapped[int] = mapped_column(ForeignKey("psyco_tests.id"))
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    test: Mapped[PsycoTest] = relationship(back_populates="results")
