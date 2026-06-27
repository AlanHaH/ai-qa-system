# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指引。

## 项目简介

基于大模型与 RAG 的学习资料智能问答系统。用户上传学习资料后，系统进行文本提取、切分、向量化和检索，用户提问时先检索相关资料片段，再调用大模型生成回答。

**当前进度**：早期开发阶段 — 仅有 FastAPI 后端基础框架和大模型 API 调用，前端（Vue3）、数据库（MySQL）、RAG 流程尚未实现。

## 技术栈

- **后端**：Python 3、FastAPI、Uvicorn
- **大模型调用**：通过 `requests` 调用 OpenAI 兼容格式 API（配置写在 `.env`）
- **前端**（待做）：Vue3、Element Plus、Axios
- **数据库**（待做）：MySQL、SQLAlchemy
- **RAG**（待做）：Chroma 或 FAISS 向量库、文本切分、Embedding

## 项目结构

```
pythonPJ/
├── backend/
│   ├── main.py          # FastAPI 入口，路由定义，ask_llm() 函数
│   ├── .env             # API_KEY、BASE_URL、MODEL_NAME（不提交到 git）
│   ├── requirements.txt # Python 依赖
│   └── venv/            # Python 虚拟环境
├── demo01.py            # 独立测试脚本（Anthropic SDK 示例）
└── AI应用开发学习路线.md  # 6 周学习计划与任务清单
```

## 常用命令

```bash
# 在 backend/ 目录下操作
cd H:\pythonPJ\backend
.\venv\Scripts\activate          # 激活虚拟环境
uvicorn main:app --reload        # 启动开发服务器（热重载）

# 访问地址
# http://127.0.0.1:8000         — 健康检查
# http://127.0.0.1:8000/docs    — Swagger 接口文档
```

## 核心架构说明

- 所有后端代码目前集中在 `backend/main.py`（单文件）
- `ask_llm(question)` 是核心函数，通过 OpenAI 兼容格式调用大模型：`POST {BASE_URL}/chat/completions`
- API 返回解析路径：`result["choices"][0]["message"]["content"]`
- `.env` 存储 `API_KEY`、`BASE_URL`、`MODEL_NAME`，通过 `python-dotenv` 加载
- `Authorization` 请求头直接发送原始 key，不带 `Bearer ` 前缀（与当前 API 提供商格式一致）

## 后续规划架构（来自学习路线）

重构后的目标目录结构：
- `routers/` — FastAPI 路由处理
- `services/` — 业务逻辑（llm_service.py、rag_service.py）
- `models/` — SQLAlchemy 数据库模型
- `schemas/` — Pydantic 请求/响应模型

RAG 流程：文档上传 → 文本提取 → 切分（500 字符，50 重叠）→ Embedding → 存入向量库 → 查询向量 → 相似度检索 → 拼接 Prompt → 大模型生成回答

## 语言说明

本项目为中文学习项目，注释、文档、界面均使用中文，代码变量名和函数名使用英文。
