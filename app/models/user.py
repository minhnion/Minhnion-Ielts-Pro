from sqlalchemy import (Column, Integer, String, Boolean, DateTime, Float, 
                        ForeignKey, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

user_saved_words = Table(
    'user_saved_words',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('word_id', Integer, ForeignKey('vocabulary_words.id'), primary_key=True),
    Column('saved_at', DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_attempts = relationship("TestAttempt", back_populates="user")
    saved_words = relationship("VocabularyWord", secondary=user_saved_words, back_populates="saved_by_users")

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    band_score = Column(Float, nullable=False)
    duration_seconds = Column(Integer)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))

    user = relationship("User", back_populates="test_attempts")
    test = relationship("Test", back_populates="attempts")
    user_answers = relationship("UserAnswer", back_populates="attempt")

class UserAnswer(Base):
    __tablename__ = "user_answers"
    id = Column(Integer, primary_key=True, index=True)
    user_answer = Column(String)
    is_correct = Column(Boolean, nullable=False)
    
    attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    test_question_id = Column(Integer, ForeignKey("test_questions.id"))
    
    attempt = relationship("TestAttempt", back_populates="user_answers")
    question = relationship("TestQuestion", back_populates="user_answers")