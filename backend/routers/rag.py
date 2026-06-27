from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.rag_service import search_similar
from services.llm_service import ask_llm_stream

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RAGRequest(BaseModel):
    question: str


@router.post("/rag/chat")
def rag_chat(request: RAGRequest, db: Session = Depends(get_db)):
    """
    RAG 问答接口：
    1. 根据问题检索相关文档片段
    2. 把片段拼接成 Prompt
    3. 调用大模型生成回答
    """
    # 第1步：检索相关片段
    chunks = search_similar(request.question, top_k=3)

    if not chunks:
        return {"answer": "没有找到相关资料，请先上传文档。"}

    # 第2步：拼接 Prompt
    context = "\n\n".join(chunks)
    prompt = f"""请根据以下资料回答用户的问题。如果资料中没有相关内容，请说"资料中没有找到相关信息"。

相关资料：
{context}

用户问题：{request.question}"""

    # 第3步：流式调用大模型
    def generate():
        full_answer = ""
        for chunk in ask_llm_stream(prompt):
            full_answer += chunk
            yield f"data: {chunk}\n\n"
        # 保存到数据库
        record = ChatRecord(question=request.question, answer=full_answer)
        db.add(record)
        db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/rag/chunks")
def get_chunks():
    """查看向量库中的所有文档片段"""
    from services.rag_service import collection
    data = collection.get()
    return {
        "total": len(data["ids"]),
        "chunks": [
            {
                "id": data["ids"][i],
                "content": data["documents"][i][:200] + "..." if len(data["documents"][i]) > 200 else data["documents"][i]
            }
            for i in range(len(data["ids"]))
        ]
    }
