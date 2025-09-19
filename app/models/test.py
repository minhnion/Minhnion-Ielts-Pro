from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String)
    type = Column(String, default="Academic") # Academic or General

    passages = relationship("ReadingPassage", back_populates="test")
    attempts = relationship("TestAttempt", back_populates="test")

class TestQuestion(Base):
    __tablename__ = "test_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text)
    
    passage_id = Column(Integer, ForeignKey("reading_passages.id"))
    question_type_id = Column(Integer, ForeignKey("question_types.id"))
    
    passage = relationship("ReadingPassage", back_populates="test_questions")
    question_type = relationship("QuestionType", back_populates="test_questions")
    user_answers = relationship("UserAnswer", back_populates="question")