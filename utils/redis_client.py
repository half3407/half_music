import redis
import os
import json
from typing import Any, Optional


# 创建一个连接池，全局复用
redis_pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True   # Redis 直接返回字符串
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    # 从缓存取数据，自动 JSON 解析
    value = r.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value   # 非 JSON 字符串原样返回

def set_cache(key: str, value: Any, expire: int = 300) -> None:
    # 将数据以 JSON 格式存入缓存，设置过期时间（秒）
    try:
        serialized = json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        # 如果遇到不能序列化的类型，强制转字符串
        serialized = json.dumps(value, ensure_ascii=False, default=str)
    r.set(key, serialized, ex=expire)

def delete_pattern(pattern: str) -> None:
    # 删除所有匹配 pattern 的键
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)