# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

基于大模型与 RAG 的学习资料智能问答系统。用户上传学习资料后，系统进行文本提取、切分、向量化和检索，用户提问时先检索相关资料片段，再调用大模型生成回答。

**当前进度**：核心功能已完成 — FastAPI 后端、Vue3 前端、MySQL 数据库、RAG 流程、用户认证、对话记忆、会话管理均已实现。

## 技术栈

- **后端**：Python 3、FastAPI、Uvicorn
- **前端**：Vue3、Element Plus、Axios、Pinia、Vue Router
- **数据库**：MySQL、SQLAlchemy
- **向量库**：ChromaDB（自带 Embedding）
- **大模型调用**：通过 `requests` 调用 OpenAI 兼容格式 API（配置写在 `.env`）
- **认证**：JWT（python-jose）+ bcrypt 密码加密

## 常用命令

```powershell
# 后端（在 backend/ 目录下）
cd H:\pythonPJ\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload

# 前端（在 frontend/ 目录下）
cd H:\pythonPJ\frontend
npm run dev

# 访问地址
# http://127.0.0.1:8000       — 后端健康检查
# http://127.0.0.1:8000/docs  — Swagger 接口文档
# http://localhost:5173        — 前端页面
```

### 一键启动 / 停止（推荐）

项目根目录有 `start.bat` 和 `stop.bat`，双击即可：

- `start.bat` — 同时启动后端 + 前端，并自动打开浏览器
- `stop.bat` — 结束占用 8000 / 5173 端口的进程

> ⚠️ 这两个 `.bat` 文件是 **GBK 编码 + CRLF 行尾**（中文 Windows cmd 默认按 GBK 解析）。
> 用编辑器修改后**不要另存为 UTF-8**，否则中文会乱码、命令解析错乱。

## 项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # FastAPI 入口，挂载路由
│   ├── database.py          # SQLAlchemy 数据库连接配置
│   ├── models.py            # 数据表模型（ChatRecord, Document, User）
│   ├── .env                 # API_KEY、BASE_URL、MODEL_NAME（不提交到 git）
│   ├── routers/
│   │   ├── chat.py          # 聊天接口（普通问答、流式问答、历史记录）
│   │   ├── doc.py           # 文档接口（上传、列表、删除）
│   │   ├── rag.py           # RAG 问答接口（带引用片段）
│   │   └── user.py          # 用户接口（注册、登录、获取用户信息）
│   └── services/
│       ├── llm_service.py   # 大模型调用（普通 + 流式 + 历史压缩）
│       ├── doc_service.py   # 文档文本提取（PDF/txt/md）
│       ├── rag_service.py   # RAG 服务（切分、向量库、检索）
│       └── auth_service.py  # 认证服务（密码加密、JWT）
├── frontend/
│   ├── src/
│   │   ├── main.js          # 入口（挂载 Pinia、Router、Element Plus）
│   │   ├── api.js           # Axios 实例（自动带 token）
│   │   ├── components/
│   │   │   └── ChatSidebar.vue  # 左侧对话列表
│   │   ├── router/index.js  # 路由配置（含路由守卫）
│   │   ├── stores/
│   │   │   ├── user.js      # 用户状态（Pinia）
│   │   │   └── chat.js      # 聊天状态（Pinia，会话管理）
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面（普通 + RAG + 引用片段）
│   │       ├── Docs.vue     # 知识库管理页面
│   │       ├── VectorDB.vue # 向量库可视化页面
│   │       └── Login.vue    # 登录注册页面
│   └── package.json
└── 复盘/                    # 每日学习复盘文档
```

## 核心架构

### 后端架构

- `main.py` 只负责挂载路由，不包含业务逻辑
- `routers/` 定义接口，处理请求参数和响应格式
- `services/` 封装业务逻辑，供 routers 调用
- `models.py` 定义 SQLAlchemy 数据表模型
- `database.py` 配置数据库连接（MySQL + SQLAlchemy）

### 前端架构

- `views/` 页面组件，每个页面独立
- `stores/` Pinia 状态管理（user.js 用户状态、chat.js 聊天状态）
- `api.js` Axios 实例，请求拦截器自动带 token
- `components/` 共用组件（ChatSidebar）
- `router/index.js` 路由配置，含路由守卫（未登录跳转登录页）

### RAG 流程

```
上传文档 → 文本提取 → 切分（500字符，50重叠）→ 存入 ChromaDB 向量库
用户提问 → 语义检索（取前3个片段）→ 拼接 Prompt → 大模型生成回答
```

### 对话记忆

- 前端发送最近 10 条历史记录
- 后端检查：超过 5 条则压缩旧历史（调用 AI 生成摘要）
- 发送给大模型：摘要 + 最近 5 条 + 当前问题

### 用户认证

- JWT token 存储用户 ID（字符串格式）
- 前端 localStorage 持久化 token
- Axios 请求拦截器自动带上 `Authorization: Bearer {token}`
- 后端通过 `Header(None)` 获取 token 并解析用户 ID

### 会话管理

- Pinia store 管理会话列表和当前会话
- localStorage 按用户 ID 隔离（key 带 userId）
- 切换页面不丢失数据（Pinia 状态）
- 退出登录时保存当前会话

## 注意事项

- `.env` 存储密钥，不提交到 git
- `chroma_db/` 向量库数据不提交到 git
- `backend/venv/` 和 `frontend/node_modules/` 不提交到 git
- JWT 的 `sub` 字段必须是字符串（`str(user.id)`）
- 流式响应用 `fetch`（Axios 不支持 ReadableStream）
- CORS 已配置允许所有来源（开发环境）

## 语言说明

本项目为中文学习项目，注释、文档、界面均使用中文，代码变量名和函数名使用英文。
