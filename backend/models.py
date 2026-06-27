from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class ChatRecord(Base):
    __tablename__ = "chat_record"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False, comment="文件名")
    content = Column(Text, nullable=False, comment="提取的文本内容")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")

