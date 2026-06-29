from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.llm_service import ask_llm, ask_llm_stream
from services.auth_service import get_current_user_id

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


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
    # 支持 "Bearer token" 和直接传 token 两种格式
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    return get_current_user_id(token)


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), authorization: str = Header(None)):
    user_id = get_user_id(authorization)
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

    def generate():
        full_answer = ""
        try:
            for chunk in ask_llm_stream(request.question):
                full_answer += chunk
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: 错误: {str(e)}\n\n"
        finally:
            # 流结束后保存到数据库
            if full_answer:
                try:
                    db = SessionLocal()
                    record = ChatRecord(user_id=user_id or 0, question=request.question, answer=full_answer)
                    db.add(record)
                    db.commit()
                    db.close()
                except Exception:
                    pass  # 保存失败不影响用户体验
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
