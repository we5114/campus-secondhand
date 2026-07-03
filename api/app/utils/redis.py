"""
Redis工具类
"""
import redis.asyncio as redis
from typing import Optional
import json

from app.config.settings import settings

# Redis连接池
redis_pool: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """获取Redis连接"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
    return redis_pool


async def init_redis():
    """初始化Redis连接"""
    global redis_pool
    redis_pool = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50
    )


async def close_redis():
    """关闭Redis连接"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None


async def set_key(key: str, value: str, expire: int = 0):
    """设置键值"""
    r = await get_redis()
    if expire > 0:
        await r.setex(key, expire, value)
    else:
        await r.set(key, value)


async def get_key(key: str) -> Optional[str]:
    """获取键值"""
    r = await get_redis()
    return await r.get(key)


async def delete_key(key: str):
    """删除键"""
    r = await get_redis()
    await r.delete(key)


async def set_json(key: str, value: dict, expire: int = 0):
    """设置JSON数据"""
    r = await get_redis()
    json_str = json.dumps(value, ensure_ascii=False)
    if expire > 0:
        await r.setex(key, expire, json_str)
    else:
        await r.set(key, json_str)


async def get_json(key: str) -> Optional[dict]:
    """获取JSON数据"""
    r = await get_redis()
    value = await r.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return None


async def incr_key(key: str, amount: int = 1) -> int:
    """自增键值"""
    r = await get_redis()
    return await r.incrby(key, amount)


async def expire_key(key: str, seconds: int):
    """设置过期时间"""
    r = await get_redis()
    await r.expire(key, seconds)


async def exists_key(key: str) -> bool:
    """检查键是否存在"""
    r = await get_redis()
    return await r.exists(key) > 0
