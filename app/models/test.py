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

class ReadingPassage(Base):
    __tablename__ = "reading_passages"
    id = Column(Integer, primary_key=True, index=True)
    passage_text = Column(Text, nullable=False)
    order_in_test = Column(Integer, nullable=False) # 1, 2, or 3
    
    test_id = Column(Integer, ForeignKey("tests.id"))
    
    test = relationship("Test", back_populates="passages")
    questions = relationship("TestQuestion", back_populates="passage")

class TestQuestion(Base):
    __tablename__ = "test_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text)
    
    passage_id = Column(Integer, ForeignKey("reading_passages.id"))
    question_type_id = Column(Integer, ForeignKey("question_types.id"))
    
    passage = relationship("ReadingPassage", back_populates="questions")
    question_type = relationship("QuestionType", back_populates="test_questions")
    user_answers = relationship("UserAnswer", back_populates="question")