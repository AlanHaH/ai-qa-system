from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from database import SessionLocal
from models import ChatRecord
from services.rag_service import search_similar
from services.llm_service import ask_llm_stream
from services.auth_service import get_current_user_id

router = APIRouter()


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


class RAGRequest(BaseModel):
    question: str


@router.post("/rag/chat")
def rag_chat(request: RAGRequest, authorization: str = Header(None)):
    """RAG 问答接口"""
    user_id = get_user_id(authorization)

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
        # 先发送引用片段
        import json
        refs = json.dumps({"type": "references", "chunks": chunks}, ensure_ascii=False)
        yield f"data: {refs}\n\n"

        full_answer = ""
        try:
            for chunk in ask_llm_stream(prompt):
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
                    pass
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
