# core/models/psyco_test_with_correct_answer.py

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Integer, String, ForeignKey

from .base import Base


class PycoTestWithCorrectAnswer(Base):
    __tablename__ = "pyco_tests_with_correct_answer"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    questions: Mapped[list["PsycoQuestionWithCorrectAnswer"]] = relationship(back_populates="test", cascade="all, delete-orphan")
    results: Mapped[list["PsycoResultWithFromToGroup"]] = relationship(back_populates="test", cascade="all, delete-orphan")

class PsycoQuestionWithCorrectAnswer(Base):
    __tablename__ = "psyco_questions_with_correct_answer"

    question_text: Mapped[str] = mapped_column(String, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("pyco_tests_with_correct_answer.id"))

    test: Mapped[PycoTestWithCorrectAnswer] = relationship(back_populates="questions")
    answers: Mapped[list["PsycoAnswerWithCorrectMarker"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class PsycoAnswerWithCorrectMarker(Base):
    __tablename__ = "psyco_answers_with_correct_marker"

    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("psyco_questions_with_correct_answer.id"))

    question: Mapped[PsycoQuestionWithCorrectAnswer] = relationship(back_populates="answers")


class PsycoResultWithFromToGroup(Base):
    __tablename__ = "psyco_results_with_from_to_group"

    test_id: Mapped[int] = mapped_column(ForeignKey("pyco_tests_with_correct_answer.id"))
    min_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    test: Mapped[PycoTestWithCorrectAnswer] = relationship(back_populates="results")