from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ReadingPassage(Base):
    __tablename__ = "reading_passages"

    id = Column(Integer, primary_key=True, index=True)
    title =Column(String, nullable=True)
    content = Column(Text, nullable=False)

    practice_questions = relationship("PracticeQuestion", back_populates="passage")
    test_questions = relationship("TestQuestion", back_populates="passage")
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=True)
    test = relationship("Test", back_populates="passages")
