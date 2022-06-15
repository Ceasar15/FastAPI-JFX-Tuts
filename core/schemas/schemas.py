from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookSchema(BaseModel):
    title: str
    author: str
    price: int
    description: str

    class Config:
        orm_mode = True


class ShowBookSchema(BaseModel):
    id: Optional[int]
    title: Optional[str]
    author: Optional[str]
    price: Optional[int]
    description: Optional[str]
    time_created: Optional[datetime]

    class Config:
        orm_mode = True
