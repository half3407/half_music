# Half Music 🎵

基于 **FastAPI** 的音乐流媒体平台后端 API，提供用户管理、歌曲管理、歌单管理、评论以及文件上传等功能。

## ✨ 功能特性

- **用户系统**：注册、登录，基于 JWT 的身份认证，bcrypt 密码加密，普通用户 / 管理员角色权限控制；注册通过数据库唯一约束 + `IntegrityError` 回滚兜底，避免并发下重复用户名
- **歌曲管理**：歌曲的增删改查、按歌名 / 歌手模糊搜索（创建、修改、删除需管理员权限）
- **歌单管理**：创建、修改、删除歌单，歌单收藏，向歌单中添加 / 移除歌曲，按收藏数排序
- **评论功能**：对歌曲发表评论、查看与删除评论（评论不可修改）
- **文件上传**：歌曲封面、音频文件、用户头像上传，带类型与大小校验，静态文件服务
- **缓存加速**：基于 Redis 的 cache-aside 缓存，列表 / 详情接口带 TTL 缓存，写操作按 key pattern 精准失效
- **容器化部署**：提供 Dockerfile 与 docker-compose，一键拉起「应用 + Redis」，数据卷持久化
- **通用能力**：统一分页、软删除（`deleted_at`）、自动时间戳（`created_at` / `updated_at`）、日志轮转、数据库迁移

## 🛠 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ASGI 服务器 | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 缓存 | Redis |
| 数据迁移 | Alembic |
| 容器化 | Docker / Docker Compose |
| 配置管理 | pydantic-settings |
| 认证 | PyJWT (HS256) |
| 密码加密 | bcrypt |
| 日志 | loguru |
| 测试 | pytest + FastAPI TestClient |

## 📁 项目结构

```
half_music/
├── main.py                 # 应用入口，注册路由、挂载静态文件、初始化数据库
├── config.py               # 全局配置（JWT / 日志 / 分页 / 文件上传）
├── log.py                  # loguru 日志初始化
├── alembic.ini             # Alembic 配置
├── .env.template           # 环境变量模板
├── requirements.txt        # Python 依赖清单
├── Dockerfile              # 应用镜像构建
├── docker-compose.yml      # 应用 + Redis 编排
├── controls/               # 路由控制层（业务接口）
│   ├── ctl_user.py         #   用户管理
│   ├── ctl_song.py         #   歌曲管理
│   ├── ctl_playlist.py     #   歌单管理
│   ├── ctl_comment.py      #   评论功能
│   └── ctl_file.py         #   文件上传
├── models/                 # 数据模型层（SQLAlchemy ORM + Pydantic）
│   ├── base.py             #   基类、时间戳 Mixin、软删除 Mixin
│   ├── user.py             #   用户
│   ├── song.py             #   歌曲
│   ├── playlist.py         #   歌单
│   ├── comment.py          #   评论
│   └── association.py      #   歌单-歌曲多对多关联表
├── deps/                   # 依赖注入
│   ├── database.py         #   数据库会话
│   ├── permissions.py      #   权限校验依赖
│   └── pagination.py       #   分页参数
├── db/
│   ├── db_server.py        #   数据库引擎与会话工厂、建表
│   └── db_update.py        #   数据库更新脚本
├── utils/
│   ├── token.py            #   JWT 生成与解析
│   ├── security.py         #   bcrypt 密码哈希与校验
│   └── redis_client.py     #   Redis 连接池与缓存读写 / 失效工具
├── alembic/                # 数据库迁移脚本
└── tests/                  # 测试用例
    ├── conftest.py         #   测试夹具（内存数据库、token）
    ├── test_user.py
    ├── test_song.py
    ├── test_playlist.py
    └── test_concurrent.py
```

## 🚀 快速开始

> 推荐使用 [Docker 部署](#-docker-部署) 一键拉起「应用 + Redis」；若想本地直接运行，按下方步骤操作。

### 1. 环境要求

- Python 3.11+
- Redis（本地运行缓存功能时需要，可用 `docker run -p 6379:6379 redis` 快速启动）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.template` 为 `.env` 并按需修改：

```bash
cp .env.template .env
```

主要配置项（详见 [config.py](config.py)）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MUSIC_SERVER_HOST` | 服务器主机 | `localhost` |
| `MUSIC_SERVER_PORT` | 服务器端口 | `8000` |
| `MUSIC_ROOT_ROUTER_PREFIX` | 根路由前缀 | `/api/v1` |
| `JWT_SECRET` | JWT 加解密密钥 | 内置默认值（生产环境务必修改） |
| `JWT_TOKEN_EXPIRE_TIME` | Token 有效期（秒） | `7200` |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `UPLOAD_DIR` | 文件上传根目录 | `/py_codes/half_music_upload/` |
| `MAX_UPLOAD_SIZE` | 单文件最大字节数 | `20971520`（20 MB） |
| `STATIC_URL_PREFIX` | 静态文件挂载前缀 | `/static` |
| `REDIS_HOST` | Redis 主机地址 | `localhost`（容器内为 `redis`） |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `MUSIC_LOG_*` | 日志路径 / 等级 / 轮转 / 保留天数 | 见配置 |
| `PAGE_*` | 分页默认值 / 上下限 | 见配置 |

### 4. 启动服务

```bash
python main.py
```

启动后访问：

- API 文档（Swagger UI）：http://localhost:8000/docs
- API 文档（ReDoc）：http://localhost:8000/redoc

## 📖 API 概览

所有接口均以根路由前缀 `/api/v1` 开头。需要认证的接口请在请求头中携带 `Authorization: Bearer <token>`。

### 用户管理 `/users`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/register` | 用户注册 | 公开 |
| POST | `/login` | 用户登录，返回 JWT | 公开 |
| POST | `/view_all_user` | 查看所有用户基本信息（分页） | 公开 |
| POST | `/search_user` | 模糊搜索用户名（分页） | 公开 |
| POST | `/view_single_user/{user_id}` | 查看用户详情 | 本人或管理员 |
| POST | `/update_user/{user_id}` | 修改用户信息 | 本人或管理员 |
| POST | `/delete_user/{user_id}` | 注销用户（可选是否删除其歌单） | 本人或管理员 |

### 歌曲管理 `/songs`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/create` | 创建歌曲 | 管理员 |
| POST | `/update/{song_id}` | 修改歌曲信息 | 管理员 |
| POST | `/delete/{song_id}` | 删除歌曲 | 管理员 |
| POST | `/view_all` | 查看所有歌曲（按创建时间倒序，分页） | 公开 |
| POST | `/search_song` | 模糊搜索歌名 / 歌手（分页） | 公开 |
| POST | `/view_single/{song_id}` | 查看歌曲详情 | 公开 |
| POST | `/add_to_playlist/{song_id}/{playlist_id}` | 添加歌曲到歌单 | 歌单创建者 |
| POST | `/delete_from_playlist/{song_id}/{playlist_id}` | 从歌单移除歌曲 | 歌单创建者 |

### 歌单管理 `/playlists`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/create` | 创建歌单 | 登录用户 |
| POST | `/view_all` | 查看所有歌单（按收藏数倒序，分页） | 公开 |
| POST | `/search_playlist` | 模糊搜索歌单名（分页） | 公开 |
| POST | `/view_single/{playlist_id}` | 查看歌单详情（含歌曲列表） | 公开 |
| POST | `/collect/{playlist_id}` | 收藏歌单 | 登录用户 |
| POST | `/update/{playlist_id}` | 修改歌单信息 | 创建者或管理员 |
| POST | `/delete/{playlist_id}` | 删除歌单 | 创建者或管理员 |

### 评论功能 `/comments`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/create` | 发表评论 | 登录用户 |
| POST | `/delete/{comment_id}` | 删除评论 | 创建者或管理员 |
| POST | `/view_all/{song_id}` | 查看某歌曲下所有评论（分页） | 公开 |
| POST | `/view/{comment_id}` | 查看评论详情 | 公开 |

### 文件管理 `/files`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/cover` | 上传歌单 / 歌曲封面 | 管理员 |
| POST | `/song` | 上传音频文件 | 管理员 |
| POST | `/avatar` | 上传用户头像 | 登录用户 |

上传成功后返回可访问的静态 URL，文件通过 `STATIC_URL_PREFIX` 对外提供访问（如 `/static/covers/xxx.jpg`）。

## 🔐 认证流程

1. 调用 `/users/register` 注册账号
2. 调用 `/users/login` 登录，获取 `access_token`
3. 在后续请求头中携带：`Authorization: Bearer <access_token>`

Token 使用 HS256 算法签名，载荷包含 `user_id`、`role` 和过期时间 `exp`，默认有效期 2 小时。

## ⚡ 缓存策略

读多写少的列表 / 详情接口接入 Redis，采用经典的 **cache-aside（旁路缓存）** 模式：

- **读**：先查缓存命中则直接返回；未命中则查数据库、写回缓存并设置 TTL（默认 300 秒）。
- **写**：歌曲 / 歌单的增删改会按 key pattern 精准失效相关缓存（如 `delete_pattern("song:page:*")`），保证数据一致性，避免脏读。
- **Key 设计**：以业务维度 + 分页参数组织，例如 `songs:page:{page}:size:{size}`、`playlist:{id}`。

缓存读写与失效封装在 [utils/redis_client.py](utils/redis_client.py)，对外暴露 `get_cache` / `set_cache` / `delete_pattern`，并通过连接池复用连接。值以 JSON 序列化存储。

## 🐳 Docker 部署

项目提供 [Dockerfile](Dockerfile) 与 [docker-compose.yml](docker-compose.yml)，一条命令即可拉起「应用 + Redis」：

```bash
docker compose up -d --build
```

启动后同样通过 http://localhost:8000/docs 访问。compose 编排说明：

- `app` 服务由本地 Dockerfile 构建，通过环境变量 `REDIS_HOST=redis` 连接同网络下的 Redis 容器。
- `redis` 服务使用官方镜像，与 `app` 处于同一 bridge 网络 `music_net`。
- 上传目录与 SQLite 数据库通过数据卷（`./upload`、`./data`）挂载到容器外，实现持久化。

停止并清理：

```bash
docker compose down
```

## 🗄 数据库迁移

项目使用 Alembic 管理数据库结构变更：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head
```

> 应用启动时 `main.py` 会调用 `init_db()` 自动建表，便于本地快速运行。

## 🧪 运行测试

测试使用内存 SQLite 数据库，互不污染：

```bash
pytest
```

测试覆盖用户、歌曲、歌单的核心接口；[tests/test_concurrent.py](tests/test_concurrent.py) 用线程池模拟同一用户名并发注册，验证唯一约束下的兜底逻辑（见 [tests/](tests/)）。

## 📝 说明

- 默认数据库为 SQLite（`music.db`），适合开发与演示。
- CORS 默认允许来源 `http://localhost:5173`（前端开发服务器），可在 [main.py](main.py) 中调整。
- 生产部署前请务必修改 `JWT_SECRET` 等敏感配置。
