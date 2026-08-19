import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, doc, rag, session, user
from database import engine, Base
import models

# 读取.env文件配置
load_dotenv()

# 创建FastAPI应用
app = FastAPI()


@app.on_event("startup")
def init_db():
    """启动时自动建表（幂等，已存在的表不受影响）"""
    Base.metadata.create_all(engine)

# 允许跨域（前端在5173端口，后端在8000端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有来源
    allow_methods=["*"],      # 允许所有请求方法
    allow_headers=["*"],      # 允许所有请求头
)

# 挂载路由
app.include_router(chat.router)
app.include_router(doc.router)
app.include_router(rag.router)
app.include_router(session.router)
app.include_router(user.router)
@app.get("/")
def home():
    return {
        "message": "AI 学习资料智能问答系统后端启动成功"
    }

if __name__ == "__main__":
    import uvicorn
    # 支持直接运行 python main.py，或在 PyCharm 里用绿色按钮启动
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
