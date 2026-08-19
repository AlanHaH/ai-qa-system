import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 连接从 .env 的 DATABASE_URL 读取，避免密钥硬编码进 git
load_dotenv()
# 格式：mysql+pymysql://用户名:密码@地址:端口/数据库名
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ai_qa:aiqa123456@localhost:3306/ai_qa")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
