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
