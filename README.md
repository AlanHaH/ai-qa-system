# AI 学习资料智能问答系统

基于大模型与 RAG 的学习资料智能问答系统。用户上传学习资料后，系统进行文本提取、切分、向量化和语义检索；提问时先检索相关资料片段（带引用来源），再调用大模型生成回答。支持联网搜索、多会话管理、用户隔离，可一键 Docker 部署。

## ✨ 核心功能

| 模块 | 功能 |
|------|------|
| 💬 智能问答 | 普通问答（流式输出）+ Markdown 渲染 |
| 📚 RAG 问答 | 基于知识库的问答，**引用片段来源**展示 |
| 🌐 联网搜索 | 模型通过 function calling 自动决定是否搜索（Tavily），前端一键开关 |
| 🕐 时间感知 | 手写 `current_time` 工具，模型可获取当前时间辅助回答 |
| 👤 用户系统 | 注册 / 登录（JWT + bcrypt），接口强制认证（401） |
| 💾 会话管理 | 多会话持久化到数据库，按用户隔离，刷新不丢失 |
| 🧠 对话记忆 | 历史记录超过阈值自动压缩（AI 生成摘要） |
| 📄 文档管理 | 上传 PDF / txt / md，文本提取、切分、自动入向量库 |
| 🔍 向量库可视化 | 查看向量库中的切片数据与检索效果 |
| 🚀 Docker 部署 | 前后端 + MySQL 三容器编排，一键启动 |

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3、FastAPI、Uvicorn、**LangChain** |
| 前端 | Vue3、Element Plus、Pinia、Vue Router、Vite |
| 数据库 | MySQL、SQLAlchemy |
| 向量库 | ChromaDB（all-MiniLM-L6-v2 embedding） |
| 大模型 | OpenAI 兼容 API（默认 DeepSeek，可切换） |
| 联网搜索 | Tavily Search API |
| 认证 | JWT（python-jose）+ bcrypt |

## 项目结构

```
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口，挂载路由，启动建表
│   ├── database.py             # SQLAlchemy 数据库连接
│   ├── models.py               # 数据表（User, ChatSession, ChatSessionMessage, Document）
│   ├── .env                    # API_KEY、BASE_URL、MODEL_NAME、TAVILY_API_KEY（不入库）
│   ├── routers/
│   │   ├── chat.py             # 聊天接口（普通、流式、历史、联网分支）
│   │   ├── doc.py              # 文档接口（上传、列表、删除）
│   │   ├── rag.py              # RAG 问答接口（带引用片段）
│   │   ├── session.py          # 会话接口（增删改查、迁移）
│   │   └── user.py             # 用户接口（注册、登录、用户信息）
│   └── services/
│       ├── llm_service.py      # LangChain 大模型调用（普通/流式/工具调用/压缩）
│       ├── rag_service.py      # RAG（切分、向量库、检索、用户隔离）
│       ├── web_search_service.py # Tavily 搜索工具 + 时间工具（@tool）
│       ├── doc_service.py      # 文档文本提取（PDF/txt/md）
│       ├── auth_service.py     # 认证（密码加密、JWT、require_user 依赖）
│       └── prompts.py          # 提示词集中管理
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api.js              # Axios 实例（自动带 token，401 拦截）
│   │   ├── main.js             # 入口（Pinia、Router、Element Plus）
│   │   ├── router/index.js     # 路由（含登录守卫）
│   │   ├── stores/
│   │   │   ├── user.js         # 用户状态
│   │   │   └── chat.js         # 会话状态（后端持久化）
│   │   ├── utils/markdown.js   # Markdown 渲染（markdown-it + DOMPurify + 高亮）
│   │   ├── components/ChatSidebar.vue  # 会话侧边栏
│   │   └── views/              # Chat / Docs / VectorDB / Login
├── docker-compose.yml          # MySQL + 后端 + 前端（nginx）编排
├── backend/Dockerfile
├── frontend/Dockerfile
├── frontend/nginx.conf         # nginx 托管前端 + 反代后端（SSE 支持）
├── start.bat / stop.bat        # 本地一键启停
└── 复盘/                       # 每日学习复盘
```

## 快速开始（本地开发）

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 后端

```bash
cd backend

# 虚拟环境 + 依赖
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt

# 配置 .env（复制 .env.example 填写真实值）
# API_KEY=你的模型API密钥
# BASE_URL=https://api.deepseek.com
# MODEL_NAME=deepseek-v4-flash
# TAVILY_API_KEY=你的Tavily密钥

# 建库（MySQL）
# CREATE DATABASE ai_qa;  表结构启动时自动创建

# 启动
uvicorn main:app --reload
```

- 后端：http://127.0.0.1:8000
- 接口文档：http://127.0.0.1:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

- 前端：http://localhost:5173

> API 地址默认 `http://127.0.0.1:8000`，可通过环境变量 `VITE_API_BASE` 覆盖（部署时设为 `/` 走 nginx 反代）。

## Docker 部署

三服务编排：`mysql`（数据库）+ `backend`（FastAPI + LangChain）+ `frontend`（nginx 托管前端并反代后端接口）。

```bash
# 1. 服务器准备 .env（含密钥，参考 .env.example）
API_KEY=你的模型API密钥
BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-v4-flash
TAVILY_API_KEY=你的Tavily密钥

# 2. 构建并启动
docker compose up -d --build

# 3. 查看状态
docker compose ps
```

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | 前端页面，nginx 反代后端（已配置 SSE） |
| backend | 8000 | FastAPI 接口 |
| mysql | 3306（内部） | 数据库，数据持久化到卷 |

> 注意：
> - ChromaDB 首次上传文档会联网下载 embedding 模型（约 90MB）
> - `chroma_db` 向量库数据和 MySQL 数据都在数据卷中，重启不丢失
> - 换模型/换 API：只需改服务器 `.env` 后 `docker compose up -d --force-recreate backend`

## 接口文档

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/user/register` | 注册 |
| POST | `/user/login` | 登录（返回 JWT） |
| GET | `/user/me` | 当前用户信息 |
| POST | `/chat` | 普通问答（可带 use_web_search） |
| POST | `/chat/stream` | 流式问答（SSE，含联网事件） |
| GET | `/chat/history` | 聊天历史 |
| GET | `/session/list` | 会话列表 |
| GET | `/session/{session_id}` | 会话详情（含消息） |
| POST | `/session` | 创建会话 |
| PUT | `/session/{session_id}` | 更新会话 |
| DELETE | `/session/{session_id}` | 删除会话 |
| POST | `/session/migrate` | 旧 localStorage 数据迁移 |
| POST | `/doc/upload` | 上传文档 |
| GET | `/doc/list` | 文档列表 |
| DELETE | `/doc/{doc_id}` | 删除文档（同步删向量） |
| POST | `/rag/chat` | RAG 知识库问答 |
| GET | `/rag/chunks` | 查看向量库切片 |

> 除注册/登录外，接口均需 `Authorization: Bearer {token}`。

## 核心流程

```
【RAG 问答】
用户提问 → 语义检索（用户隔离，取前3片段）→ 拼接引用 → 大模型生成 → 返回带来源回答

【联网搜索】
前端开联网开关 → 模型先判断是否需搜索/查时间 → 调用工具（Tavily）→ 回填结果 → 生成回答

【对话记忆】
前端发送最近10条 → 超过5条由 AI 压缩为摘要 → 摘要 + 最近5条 + 当前问题 发给大模型

【数据隔离】
JWT 解析用户ID → 会话、文档、向量检索全部按 user_id 过滤
```

## 开发者

- [AlanKing](https://github.com/AlanHaH)
