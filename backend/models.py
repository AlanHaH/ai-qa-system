from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from database import Base

class ChatRecord(Base):
    __tablename__ = "chat_record"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, comment="用户ID")
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, comment="用户ID")
    filename = Column(String(255), nullable=False, comment="文件名")
    content = Column(LONGTEXT, nullable=False, comment="提取的文本内容")
    status = Column(String(20), nullable=False, server_default="completed", comment="向量化状态：processing/completed/failed")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密后）")
    created_at = Column(DateTime, server_default=func.now(), comment="注册时间")

class ChatSession(Base):
    __tablename__ = "chat_session"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, default=0, comment="用户ID")
    title = Column(String(255), nullable=False, default="新对话", comment="会话标题")
    old_id = Column(String(64), nullable=True, index=True, comment="迁移前的旧id(幂等去重用)")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class ChatSessionMessage(Base):
    __tablename__ = "chat_session_message"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False, index=True, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色: user/ai")
    content = Column(Text, nullable=False, comment="消息内容")
    refs = Column(JSON, nullable=True, comment="引用片段数组")
    sort_order = Column(Integer, nullable=False, default=0, comment="消息顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
