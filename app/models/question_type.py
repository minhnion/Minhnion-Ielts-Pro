from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class QuestionType(Base):
    __tablename__ = "question_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    strategy = Column(Text, nullable=True)
    test_questions = relationship("TestQuestion", back_populates="question_type")
    practice_questions = relationship("PracticeQuestion", back_populates="question_type")

class ReadingPassage(Base):
    __tablename__ = "reading_passages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    questions = relationship("PracticeQuestion", back_populates="passage")

class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)  # Store options as JSONB
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    question_type_id = Column(Integer, ForeignKey("question_types.id"))
    question_type = relationship("QuestionType", back_populates="practice_questions")
    passage = relationship("ReadingPassage", back_populates="questions")