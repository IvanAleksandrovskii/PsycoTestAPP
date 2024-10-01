# core/models/movie_quiz.py

import uuid

from sqlalchemy import String, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_storages.integrations.sqlalchemy import FileType

from core.models.base import Base
from services import movie_quiz_storage


class MovieQuiz(Base):
    __tablename__ = "movie_quizzes"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    questions: Mapped[list["MovieQuizQuestion"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")

    picture = mapped_column(FileType(storage=movie_quiz_storage))


    def __repr__(self):
        return f"MovieQuiz(text='{self.description}', id={self.id}, title='{self.title}')"
    
    def __str__(self):
        return f"MovieQuiz(title='{self.title}, id={self.id}')"


class MovieQuizQuestion(Base):
    __tablename__ = "movie_quiz_questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movie_quizzes.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)

    interesting_fact: Mapped[str] = mapped_column(Text, nullable=True)
    picture = mapped_column(FileType(storage=movie_quiz_storage))

    
    quiz: Mapped["MovieQuiz"] = relationship(back_populates="questions")
    answers: Mapped[list["MovieQuizAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"MovieQuizQuestion(text='{self.question_text}', id={self.id}, quiz_id={self.quiz_id})"
    
    def __str__(self):
        return f"'{self.question_text}'"


class MovieQuizAnswer(Base):
    __tablename__ = "movie_quiz_answers"

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movie_quiz_questions.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    question: Mapped["MovieQuizQuestion"] = relationship(back_populates="answers")

    def __repr__(self):
        return f"MovieQuizAnswer(text='{self.answer_text}', id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})"
    
    def __str__(self):
        return f"{self.answer_text}, is_correct={self.is_correct})"
