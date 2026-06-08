import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
try:
    r.ping()
    print("Redis 连接成功！")
except redis.ConnectionError:
    print("连接失败，请检查 Redis 是否启动")