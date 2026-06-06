# Half Music 前端（RhythmoTune）

基于 **Vue 3 + Vite** 的音乐播放器前端，对接本仓库的 FastAPI 后端，参考深色仪表盘设计实现。

## 技术栈

- Vue 3（`<script setup>` 组合式 API）+ Vite 6
- Vue Router 4（路由 + 登录/管理员守卫）
- Pinia（`auth` 登录态持久化、`player` 播放器状态）
- Axios（统一实例 + Bearer 注入 + 401 自动登出）

## 快速开始

> 需先启动后端（项目根目录 `python main.py`，监听 `localhost:8000`）。

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
```

开发期 Vite 已把 `/api` 与 `/static` 代理到 `http://localhost:8000`（见 `vite.config.js`），
因此前端用相对路径同源访问后端，无需关心 CORS。

构建生产包：

```bash
npm run build    # 输出到 dist/
npm run preview  # 本地预览构建产物
```

## 功能

| 模块 | 说明 |
|------|------|
| 登录 / 注册 | JWT 认证，token 持久化到 localStorage，路由守卫 |
| 首页 | 歌曲轮播、热门歌单横滑、最新歌曲网格，点击即播放 |
| 全局播放器 | 真实 `<audio>` 播放，上一首/下一首、进度拖动、音量、随机/循环 |
| 搜索 | 歌曲 + 歌单双结果，翻页 |
| 歌单详情 | 歌曲列表、收藏、（创建者/管理员）编辑删除、（创建者）增删歌曲 |
| 歌曲详情 | 信息展示 + 评论（发表 / 删除自己的评论） |
| 我的收藏 | 基于用户 `collected_playlists` 渲染，支持新建歌单 |
| 歌曲管理 | 仅管理员：歌曲增删改 + 封面/音频上传 |
| 个人设置 | 修改用户名；密码/头像因后端缺陷暂禁用并标注 |

## 目录结构

```
src/
├── api/         # 按资源拆分的接口封装（全部 POST）
├── stores/      # Pinia: auth / player
├── router/      # 路由表 + 守卫
├── components/
│   ├── layout/  # AppLayout / SideBar / TopBar
│   ├── player/  # PlayerBar
│   ├── cards/   # SongCard / PlaylistCard / FeaturedCarousel
│   └── common/  # Modal / Pager / ToastHost
├── views/       # 各页面
├── utils/       # media(静态地址解析) / toast
└── styles/      # theme.css 主题变量
```

## 与后端对接要点

- **所有后端接口均为 `POST`**（含查询/搜索），api 层已统一处理。
- 参数风格分三类：JSON body（注册/登录/创建歌曲歌单/评论）、Query（搜索/分页/删除用户）、Path（收藏/详情/增删歌单歌曲）、form-data（文件上传）。
- 静态资源地址形如 `/static/...`，由 `utils/media.js:resolveMedia` 统一解析。
- 分页响应不含总数，翻页用「是否满页」推断下一页。

## 已知后端限制（前端已规避/标注）

- `User` 模型缺 `avatar_url` 字段 → 头像上传会报错，已禁用。
- `update_user` 改密码用 MD5（登录是 bcrypt）→ 改密后无法登录，密码修改入口已禁用。
- 无「我创建的歌单」接口，「我的收藏」基于用户的 `collected_playlists` 实现。
- 后端无歌曲分类/艺术家/歌曲点赞，故设计图中相关入口未实现。

> Windows 控制台若以 GBK 运行后端，`main.py` 中的 emoji 打印会触发 `UnicodeEncodeError`，
> 可用 `set PYTHONUTF8=1` 后再启动（属后端问题，与前端无关）。
