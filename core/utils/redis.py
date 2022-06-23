import redis
import sys
import json

from core.models import models


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
        cached_book = client.setex(book[_].id, 236, data)
    print("result from db")
    return cached_book


async def delete_book_from_cache(key: str):
    return client.delete(key)
