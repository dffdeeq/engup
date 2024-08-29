from redis import asyncio as reddis
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage


def get_dispatcher(redis_url: str) -> Dispatcher:
    redis = reddis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    storage = RedisStorage(redis)
    dp = Dispatcher(storage=storage)
    return dp
