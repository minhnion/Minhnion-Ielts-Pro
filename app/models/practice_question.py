from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id"), nullable=False)
    passage = relationship("ReadingPassage", back_populates="practice_questions")
    
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)  
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    question_type_id = Column(Integer, ForeignKey("question_types.id"))
    question_type = relationship("QuestionType", back_populates="practice_questions")