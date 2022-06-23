import json

from core.schemas import schemas
from core.models import models
from core.utils import redis

from fastapi import HTTPException
from sqlalchemy.orm import Session

book_not_found = "Book not Found"


async def create_book(request: schemas.BookSchema, db: Session):
    books_from_db = models.Book(
        title=request.title,
        author=request.author,
        price=request.price,
        description=request.description,
    )
    db.add(books_from_db)
    db.commit()
    db.refresh(books_from_db)
    return books_from_db


async def get_all_books(db: Session):
    books_from_cache = redis.get_book_from_cache()
    if not books_from_cache:
        books_from_db = db.query(models.Book).all()
        await redis.set_book_in_cache(books_from_db)
        return books_from_db
    else:
        return books_from_cache


async def get_specific_book(book_id: int, db: Session):
    book_from_cache = redis.get_book_from_cache(book_id)
    if book_from_cache is None:
        book_from_db = db.query(models.Book).filter(
            models.Book.id == book_id).all()
        if not book_from_db:
            raise HTTPException(status_code=404, detail=book_not_found)
        await redis.set_book_in_cache(book_from_db)
        return book_from_db

    else:
        p = []
        book_from_cache_new = json.loads(book_from_cache.decode('utf-8'))
        p.append(book_from_cache_new)
        print("result from cache")
        return p


def edit_book(book_id: int, request: schemas.BookSchema, db: Session):
    get_book = db.query(models.Book).get(book_id)
    if not get_book:
        raise HTTPException(status_code=404, detail=book_not_found)

    db.query(models.Book).filter(models.Book.id == book_id).update({
        'title': request.title,
        'description': request.description,
        'author': request.author,
        'price': request.price,
    }, synchronize_session=False)

    db.commit()
    db.refresh(get_book)

    return get_book


async def delete_book(book_id: int, db: Session):
    get_book = db.query(models.Book).get(book_id)
    if not get_book:
        raise HTTPException(status_code=404, detail=book_not_found)

    db.delete(get_book)
    db.commit()
    await redis.delete_book_from_cache(book_id)
    return get_book
