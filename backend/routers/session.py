from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import ChatSession, ChatSessionMessage
from services.auth_service import require_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 请求体格式
class MessageIn(BaseModel):
    role: str
    content: str
    refs: Optional[List[str]] = None


class SessionCreateIn(BaseModel):
    title: Optional[str] = "新对话"
    messages: Optional[List[MessageIn]] = None


class SessionSaveIn(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[MessageIn]] = None


class MigrateItemIn(BaseModel):
    old_id: Optional[str] = None
    title: Optional[str] = "新对话"
    messages: Optional[List[MessageIn]] = None


class MigrateIn(BaseModel):
    sessions: List[MigrateItemIn] = Field(default_factory=list)


def _session_to_dict(s: ChatSession) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "created_at": str(s.created_at),
        "updated_at": str(s.updated_at),
    }


def _build_messages(db: Session, session_id: int, messages: Optional[List[MessageIn]]):
    """删除旧消息并重建（调用方负责在同一事务内）"""
    db.query(ChatSessionMessage).filter(ChatSessionMessage.session_id == session_id).delete()
    for i, msg in enumerate(messages or []):
        db.add(ChatSessionMessage(
            session_id=session_id,
            role=msg.role,
            content=msg.content,
            refs=msg.refs or [],
            sort_order=i,
        ))


@router.get("/session/list")
def session_list(db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """轻量会话列表，不含消息，按更新时间倒序"""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        .all()
    )
    return [_session_to_dict(s) for s in sessions]


@router.get("/session/{session_id}")
def session_detail(session_id: int, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """单个会话 + 全部消息"""
    s = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not s:
        return {"error": "会话不存在"}

    msgs = (
        db.query(ChatSessionMessage)
        .filter(ChatSessionMessage.session_id == session_id)
        .order_by(ChatSessionMessage.sort_order.asc(), ChatSessionMessage.id.asc())
        .all()
    )
    data = _session_to_dict(s)
    data["messages"] = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "refs": m.refs or [],
            "sort_order": m.sort_order,
            "created_at": str(m.created_at),
        }
        for m in msgs
    ]
    return data


@router.post("/session")
def session_create(payload: SessionCreateIn, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """创建会话（可带初始消息）"""
    s = ChatSession(user_id=user_id, title=payload.title or "新对话")
    db.add(s)
    db.flush()  # 拿到自增 id，未提交
    _build_messages(db, s.id, payload.messages)
    db.commit()
    db.refresh(s)
    return _session_to_dict(s)


@router.put("/session/{session_id}")
def session_save(session_id: int, payload: SessionSaveIn, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """全量覆盖保存：标题 + 消息（删除旧消息重建）"""
    s = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not s:
        return {"error": "会话不存在"}

    if payload.title is not None:
        s.title = payload.title
    if payload.messages is not None:
        _build_messages(db, session_id, payload.messages)
    # onupdate 只在行 dirty 时触发，只改消息时需要手动更新时间
    s.updated_at = func.now()
    db.commit()
    db.refresh(s)
    return _session_to_dict(s)


@router.delete("/session/{session_id}")
def session_delete(session_id: int, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """删除会话（级联删消息）"""
    s = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not s:
        return {"error": "会话不存在"}

    db.query(ChatSessionMessage).filter(ChatSessionMessage.session_id == session_id).delete()
    db.delete(s)
    db.commit()
    return {"message": "删除成功"}


@router.post("/session/migrate")
def session_migrate(payload: MigrateIn, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """批量迁移 localStorage 旧数据（按 old_id 幂等，防跨设备重复导入）"""
    mapping = {}
    for item in payload.sessions or []:
        if item.old_id:
            existing = (
                db.query(ChatSession)
                .filter(ChatSession.user_id == user_id, ChatSession.old_id == item.old_id)
                .first()
            )
            if existing:
                mapping[item.old_id] = existing.id
                continue
        s = ChatSession(user_id=user_id, title=item.title or "新对话", old_id=item.old_id)
        db.add(s)
        db.flush()
        _build_messages(db, s.id, item.messages)
        mapping[item.old_id or ""] = s.id
    db.commit()
    return {"mapping": mapping}
