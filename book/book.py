import asyncio
from calendar import c
from sqlalchemy.orm import Session
from core.schemas import schemas
from core.models import models
from fastapi import HTTPException
import redis
import sys
import json
from typing import Any

book_not_found = "Book not Found"

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


def get_book_from_cache(key=0):
    if key:
        cached_book = client.get(key)
        print("result from cache one book")
        return cached_book
    else:
        listed_result = []
        for new_key in client.scan_iter():
            listed_result.append(json.loads(
                client.get(new_key).decode('utf-8')))
        print("result from cache")
        return listed_result


async def set_book_in_cache(book: models.Book) -> bool:
    for _ in range(0, len(book)):
        data_dict = {
            "time_created": str(book[_].time_created),
            "price": book[_].price,
            "title": book[_].title,
            "id": book[_].id,
            "description": book[_].description,
            "author": book[_].author,
        }

        data = json.dumps(data_dict)
        cached_book = client.setex(book[_].id, 4, data)
    print("result from db")
    return cached_book


async def delete_book_from_cache(key: str):
    res = client.delete(key)
    print(444, res)
    return res

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
    books_from_cache = get_book_from_cache()
    if not books_from_cache:
        books_from_db = db.query(models.Book).all()
        await set_book_in_cache(books_from_db)
        return books_from_db
    else:
        return books_from_cache


async def get_specific_book(book_id: int, db: Session):
    book_from_cache = get_book_from_cache(book_id)
    if book_from_cache is None:
        book_from_db = db.query(models.Book).filter(
            models.Book.id == book_id).all()
        if not book_from_db:
            raise HTTPException(status_code=404, detail=book_not_found)
        await set_book_in_cache(book_from_db)
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
    await delete_book_from_cache(book_id)
    return get_book
