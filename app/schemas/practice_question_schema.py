from typing import List, Optional, Any
from pydantic import BaseModel
from app.schemas.reading_passage_schema import ReadingPassageSchema

class PracticeQuestionSchema(BaseModel):
    id: int
    question_text: str
    options: Optional[Any] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True
