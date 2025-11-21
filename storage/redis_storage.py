from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

redis = Redis(host = "localhost", port = 6379, db = 0)
storage = RedisStorage(redis = redis)