from pydantic import BaseModel
from typing import List, Optional
from app.schemas.practice_question import PracticeQuestionWithPassageSchema

class QuestionTypeBase(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class QuestionTypeDetailSchema(QuestionTypeBase):
    description: Optional[str] = None
    strategy: Optional[str] = None
    practice_questions: List[PracticeQuestionWithPassageSchema] = []

    class Config:
        from_attributes = True