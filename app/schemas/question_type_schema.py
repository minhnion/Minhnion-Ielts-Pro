from pydantic import BaseModel
from typing import List, Optional, Any

class ReadingPassageSchema(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    
    class Config:
        from_attributes = True

class PracticeQuestionSchema(BaseModel):
    id: int
    question_text: str
    options_data: Optional[Any] = None
    explanation: Optional[str] = None

    passage: ReadingPassageSchema 
    class Config:
        from_attributes = True

class QuestionTypeDetailSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    strategy: Optional[str] = None
    practice_questions: List[PracticeQuestionSchema] = []

    class Config:
        from_attributes = True