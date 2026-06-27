from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.llm_service import ask_llm, ask_llm_stream

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
#依赖注入:每次请求会自动创建一个数据库会话，并在请求结束后关闭它
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/chat")
def chat(request:ChatRequest,db:Session=Depends(get_db)):
    answer = ask_llm(request.question)

   # 保存到数据库
    record = ChatRecord(question=request.question, answer=answer)
    db.add(record)
    db.commit()

    return {
    "question": request.question,
    "answer": answer
    }


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """流式输出接口，逐个返回AI生成的文本片段"""

    def generate():
        full_answer = ""
        for chunk in ask_llm_stream(request.question):
            full_answer += chunk
            # SSE 格式：每个数据以 "data: " 开头，以 "\n\n" 结尾
            yield f"data: {chunk}\n\n"
        # 流结束后保存到数据库
        record = ChatRecord(question=request.question, answer=full_answer)
        db.add(record)
        db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db)):
    """查询最近20条聊天记录"""
    records = db.query(ChatRecord).order_by(ChatRecord.id.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "created_at": str(r.created_at)
        }
        for r in records
    ]

