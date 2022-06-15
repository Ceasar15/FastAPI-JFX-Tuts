from sqlalchemy.orm import Session
from core.schemas import schemas
from core.models import models
from fastapi import HTTPException


def create_book(request: schemas.BookSchema, db: Session):
    book = models.Book(
        title=request.title,
        author=request.author,
        price=request.price,
        description=request.description,
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    return book


def get_all_books(db: Session):
    books = db.query(models.Book).all()
    return books

def get_specific_book(book_id: int, db: Session):
    book = db.query(models.Book).filter(models.Book.id == book_id).all()
    return book

def edit_book(book_id: int, request: schemas.BookSchema, db: Session):
    get_book = db.query(models.Book).get(book_id)
    if not get_book:
        raise HTTPException(status_code=404, detail="Book not Found")

    db.query(models.Book).filter(models.Book.id == book_id).update({
        'title': request.title,
        'description': request.description,
        'author': request.author,
        'price': request.price,
    }, synchronize_session=False)

    db.commit()
    db.refresh(get_book)

    return get_book

def delete_book(book_id: int, db: Session):
    get_book = db.query(models.Book).get(book_id)
    if not get_book:
        raise HTTPException(status_code=404, detail="Book not Found")
    
    db.delete(get_book)
    db.commit()

    return get_book