import os
import uvicorn
import datetime
from fastapi import FastAPI
from db.db_server import DataBaseServer
from log import init_logger, logger
from controls.ctl_user import user_router
from controls.ctl_playlist import playlist_router
from controls.ctl_song import song_router
from utils.token import JWT_SECRET


MUSIC_ENVS = [env for env in os.environ if env.startswith("MUSIC_")]
MUSIC_ENV_DICT = {env: os.environ.get(env) for env in MUSIC_ENVS}
print(f"[DEBUG] 当前环境变量: {MUSIC_ENV_DICT}")


app = FastAPI()
ROOT_ROUTER_PREFIX=os.environ.get("MUSIC_ROOT_ROUTER_PREFIX","/api/v1")

#注册路由
app.include_router(user_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["用户管理"])
app.include_router(playlist_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["歌单管理"])
app.include_router(song_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["歌曲管理"])

# 初始化数据库（建表）
DataBaseServer().init_db()

if __name__ == "__main__":

    logger.info("应用启动中...")
    init_logger(f"music_{datetime.date.today()}.log")

    uvicorn.run(
        "main:app",
        host=os.environ.get("MUSIC_SERVER_HOST", "localhost"),
        port=int(os.environ.get("MUSIC_SERVER_PORT", "8000")),
    )