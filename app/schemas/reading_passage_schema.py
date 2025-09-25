from typing import Optional
from pydantic import BaseModel

class ReadingPassageSchema(BaseModel):
    id: int
    title: Optional[str] = None
    content: str
    
    class Config:
        from_attributes = True