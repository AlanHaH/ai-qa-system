# 基于大模型与 RAG 的学习资料智能问答系统

用户上传学习资料后，系统对文档进行文本提取、切分、向量化和检索，用户提问时先检索相关资料片段，再调用大模型生成更贴合资料内容的回答。

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3、FastAPI、Uvicorn |
| 前端 | Vue3、Vite |
| 数据库 | MySQL、SQLAlchemy |
| 向量库 | ChromaDB |
| 大模型 | OpenAI 兼容格式 API |

## 功能列表

### 聊天模块
- [x] 普通 AI 问答（流式输出）
- [x] RAG 知识库问答
- [x] 聊天记录保存
- [x] 聊天历史查询

### 文档模块
- [x] 上传 PDF / txt / md 文件
- [x] 文档列表展示
- [x] 删除文档
- [x] 文档文本提取
- [x] 文本切分（500 字符，50 重叠）
- [x] 自动存入向量库

### 向量库模块
- [x] 向量存储
- [x] 语义相似度检索
- [x] 向量库数据可视化

### 前端模块
- [x] 聊天页面（普通 + RAG 切换）
- [x] 知识库管理页面
- [x] 向量库可视化页面
- [x] 导航栏

## 项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # 入口，挂载路由
│   ├── database.py          # 数据库连接配置
│   ├── models.py            # 数据表模型（ChatRecord, Document）
│   ├── .env                 # API_KEY、BASE_URL、MODEL_NAME
│   ├── chroma_db/           # ChromaDB 向量库数据
│   ├── routers/
│   │   ├── chat.py          # 聊天相关接口
│   │   ├── doc.py           # 文档相关接口
│   │   └── rag.py           # RAG 问答接口
│   └── services/
│       ├── llm_service.py   # 大模型调用（普通 + 流式）
│       ├── doc_service.py   # 文档文本提取
│       └── rag_service.py   # RAG 服务（切分、向量库、检索）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 根组件（导航栏 + 路由出口）
│   │   ├── main.js          # 入口（挂载路由）
│   │   ├── router/
│   │   │   └── index.js     # 路由配置
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面
│   │       ├── Docs.vue     # 知识库管理页面
│   │       └── VectorDB.vue # 向量库可视化页面
│   └── package.json
└── README.md
```

## 快速启动

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件，写入以下内容：
# API_KEY=你的API密钥
# BASE_URL=你的API地址
# MODEL_NAME=模型名称

# 创建数据库
# 在 MySQL 中执行：CREATE DATABASE ai_qa;

# 启动服务
uvicorn main:app --reload
```

后端访问地址：http://127.0.0.1:8000
接口文档：http://127.0.0.1:8000/docs

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址：http://localhost:5173

## 接口文档

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 健康检查 |
| POST | `/chat` | 普通问答（返回完整回答） |
| POST | `/chat/stream` | 流式问答（逐字返回） |
| GET | `/chat/history` | 查询聊天历史 |
| POST | `/doc/upload` | 上传文档 |
| GET | `/doc/list` | 查询文档列表 |
| DELETE | `/doc/{id}` | 删除文档 |
| POST | `/rag/chat` | RAG 知识库问答 |
| GET | `/rag/chunks` | 查看向量库数据 |

## RAG 流程

```
【上传文档】
PDF/txt/md → 文本提取 → 切分(500字符,50重叠) → 存入向量库

【RAG 问答】
用户提问 → 语义检索(取前3个片段) → 拼接Prompt → 大模型生成回答
```

## 截图

（待添加）

## 后续计划

- [ ] 用户登录注册（JWT 认证）
- [ ] Agent 工具调用
- [ ] 部署上线

## 开发者

- [AlanKing](https://github.com/AlanHaH)
