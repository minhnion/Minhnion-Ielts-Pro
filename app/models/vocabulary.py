from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import user_saved_words

class VocabTopic(Base):
    __tablename__ = "vocab_topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text)

    words = relationship("VocabularyWord", back_populates="topic")

class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    ipa = Column(String)
    definition_vi = Column(Text, nullable=False)
    example = Column(Text)
    
    topic_id = Column(Integer, ForeignKey("vocab_topics.id"))
    
    topic = relationship("VocabTopic", back_populates="words")
    saved_by_users = relationship("User", secondary=user_saved_words, back_populates="saved_words")