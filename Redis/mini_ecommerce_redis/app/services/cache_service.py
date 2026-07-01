import json
import redis.asyncio as redis


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


CACHE_TTL_SECONDS = 60


async def get_cache(key: str):
    cached_data = await redis_client.get(key)

    if cached_data:
        return json.loads(cached_data)

    return None


async def set_cache(key: str, value: dict):
    await redis_client.setex(
        key,
        CACHE_TTL_SECONDS,
        json.dumps(value)
    )


async def delete_cache(key: str):
    await redis_client.delete(key)


async def get_cache_ttl(key: str):
    return await redis_client.ttl(key)
