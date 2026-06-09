import os
from dotenv import load_dotenv

# 把项目根目录下 .env 文件里的配置，加载进环境变量(os.environ)。
# 必须放在所有其他 import 之前：因为下面导入的某些模块(比如 utils.token)
# 在"被导入的那一刻"就会去读环境变量，如果 .env 还没加载就读，会读到空值。
load_dotenv()

from fastapi.staticfiles import StaticFiles
import uvicorn
import datetime
from fastapi import FastAPI
from db.db_server import init_db, init_first_admin
from fastapi.middleware.cors import CORSMiddleware
from log import init_logger, logger
from config import settings
from controls.ctl_user import user_router
from controls.ctl_playlist import playlist_router
from controls.ctl_song import song_router
from controls.ctl_comment import comment_router
from controls.ctl_file import file_router
from utils.token import JWT_SECRET


MUSIC_ENVS = [env for env in os.environ if env.startswith("MUSIC_")]
MUSIC_ENV_DICT = {env: os.environ.get(env) for env in MUSIC_ENVS}
print(f"[DEBUG] 当前环境变量: {MUSIC_ENV_DICT}")


app = FastAPI(
    title="Half Music API",
    description="基于 FastAPI 的音乐流媒体平台后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_ROUTER_PREFIX=os.environ.get("MUSIC_ROOT_ROUTER_PREFIX","/api/v1")

#创建文件上传目录
os.makedirs(settings.cover_dir, exist_ok=True)
os.makedirs(settings.song_dir, exist_ok=True)
os.makedirs(settings.avatar_dir, exist_ok=True)

#挂在静态文件服务
app.mount(
    settings.STATIC_URL_PREFIX + "/covers", 
    StaticFiles(directory=str(settings.cover_dir)), 
    name="covers"
)
app.mount(
    settings.STATIC_URL_PREFIX + "/songs", 
    StaticFiles(directory=str(settings.song_dir)), 
    name="songs"
)
app.mount(
    settings.STATIC_URL_PREFIX + "/avatars", 
    StaticFiles(directory=str(settings.avatar_dir)), 
    name="avatars"
)

print(f"✅ 静态文件服务已挂载到: {settings.STATIC_URL_PREFIX}")
print(f"📁 封面目录: {settings.cover_dir.absolute()}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#注册路由
app.include_router(user_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["用户管理"])
app.include_router(playlist_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["歌单管理"])
app.include_router(song_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["歌曲管理"])
app.include_router(comment_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["评论功能"])
app.include_router(file_router,prefix=f"{ROOT_ROUTER_PREFIX}",tags=["文件管理"])

# 初始化数据库（建表）
init_db()
# 建表之后，按需引导出第一个管理员（已存在管理员则自动跳过）
init_first_admin()

if __name__ == "__main__":

    logger.info("应用启动中...")
    init_logger(f"music_{datetime.date.today()}.log")

    uvicorn.run(
        "main:app",
        host=os.environ.get("MUSIC_SERVER_HOST", "localhost"),
        port=int(os.environ.get("MUSIC_SERVER_PORT", "8000")),
    )