from sqlalchemy.orm import Session
from core.schemas import schemas
from core.models import models
from fastapi import HTTPException
import redis
import sys
from datetime import timedelta
import json


# connect to redis
def connect_redis() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
        )
        ping = client.ping()
        if ping is None:
            sys.exit("Connection Error")
        else:
            return client
    except redis.exceptions.ConnectionError:
        sys.exit("Connection Error")


print("Connecting to redis...", connect_redis())


client = connect_redis()


def get_book_from_cache(key: str):
    cached_book = client.get(key)
    print("Book from cache", cached_book)
    return cached_book


def set_book_in_cache(key: str, book: models.Book):
    print("key: ", key, "book: ", book)
    cached_book = client.setex(key,  4, str(book))
    print("cached_booccck: ", cached_book)
    return cached_book


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
    book_from_cache = get_book_from_cache(book_id)
    print("book from cache:", book_from_cache)
    if book_from_cache is None:
        book_from_db = db.query(models.Book).filter(
            models.Book.id == book_id).all()
        print("book_from_db: ", book_from_db)
        # print("json:", json.dumps(book_from_db))
        set_book_in_cache(book_id, book_from_db)
        return book_from_db
    else:
        return book_from_cache


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
