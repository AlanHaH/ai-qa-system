from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.llm_service import ask_llm, ask_llm_stream, compress_history
from services.auth_service import get_current_user_id

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_id(authorization: str = Header(None)):
    """从请求头获取当前用户 ID"""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    return get_current_user_id(token)


def build_history_with_summary(history: List[ChatMessage]) -> List[dict]:
    """
    构建带摘要的历史记录。
    如果历史超过5条，旧的压缩成摘要，最近5条保留。
    """
    if not history:
        return []

    # 转成字典列表
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in history]

    # 不超过5条，直接返回
    if len(history_dicts) <= 5:
        return history_dicts

    # 超过5条：旧的压缩，最近5条保留
    old_history = history_dicts[:-5]
    recent_history = history_dicts[-5:]

    # 压缩旧历史
    summary = compress_history(old_history)

    # 构建最终历史
    result = []
    if summary:
        result.append({
            "role": "user",
            "content": f"[历史摘要] 之前我们讨论了：{summary}"
        })
        result.append({
            "role": "assistant",
            "content": "好的，我了解之前的对话内容。"
        })
    result.extend(recent_history)

    return result


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), authorization: str = Header(None)):
    user_id = get_user_id(authorization)

    # 构建带摘要的历史
    history = build_history_with_summary(request.history)

    # 调用大模型
    answer = ask_llm(request.question)

    # 保存到数据库
    record = ChatRecord(user_id=user_id or 0, question=request.question, answer=answer)
    db.add(record)
    db.commit()

    return {"question": request.question, "answer": answer}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, authorization: str = Header(None)):
    """流式输出接口"""
    user_id = get_user_id(authorization)

    # 构建带摘要的历史
    history = build_history_with_summary(request.history)

    def generate():
        full_answer = ""
        try:
            for chunk in ask_llm_stream(request.question, history=history):
                full_answer += chunk
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: 错误: {str(e)}\n\n"
        finally:
            if full_answer:
                try:
                    db = SessionLocal()
                    record = ChatRecord(user_id=user_id or 0, question=request.question, answer=full_answer)
                    db.add(record)
                    db.commit()
                    db.close()
                except Exception:
                    pass
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), authorization: str = Header(None)):
    """查询当前用户的聊天记录"""
    user_id = get_user_id(authorization)
    if not user_id:
        return []

    records = db.query(ChatRecord).filter(
        ChatRecord.user_id == user_id
    ).order_by(ChatRecord.id.desc()).limit(20).all()

    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "created_at": str(r.created_at)
        }
        for r in records
    ]
