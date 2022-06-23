from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session

from core.schemas import schemas
from core.database.database import get_db
from book import book

router = APIRouter(tags=["book"], prefix="/book")

# create books
@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.BookSchema)
async def create_book(request: schemas.BookSchema, db: Session = Depends(get_db)):
    return await book.create_book(request, db)


# get all books
@router.get(
    "/get_all_books", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowBookSchema]
)
async def get_all_books(db: Session = Depends(get_db)):
    return await book.get_all_books(db)

# get specific book
@router.get(
    "/get_book/{book_id}", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowBookSchema]
)
async def get_specific_book(book_id: str, db: Session = Depends(get_db)):
    return await book.get_specific_book(book_id, db)


# edit stats of a book
@router.patch("/edit_book/{book_id}", status_code=status.HTTP_200_OK, response_model=schemas.ShowBookSchema)
def update_book(book_id: str, request: schemas.ShowBookSchema, db: Session = Depends(get_db)):
    return book.edit_book(book_id, request, db)


# delete stats of a game
@router.delete("/delete_book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stats_of_game(book_id: int, db: Session = Depends(get_db)):
    return book.delete_book(book_id, db)
