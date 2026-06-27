from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 连接格式：mysql+pymysql://用户名:密码@地址:端口/数据库名
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/ai_qa"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
