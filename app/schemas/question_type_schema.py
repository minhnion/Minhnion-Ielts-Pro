from pydantic import BaseModel
from typing import List, Optional

from app.schemas.practice_question_schema import PracticeQuestionSchema
from app.schemas.reading_passage_schema import ReadingPassageSchema

class QuestionTypeBase(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class PracticeSetGroupedSchema(BaseModel):
    passage: ReadingPassageSchema
    questions: List[PracticeQuestionSchema]

    class Config:
        from_attributes = True

class QuestionTypeDetailGroupedSchema(QuestionTypeBase):
    description: Optional[str] = None
    strategy: Optional[str] = None
    practice_sets: List[PracticeSetGroupedSchema] = []

    class Config:
        from_attributes = True