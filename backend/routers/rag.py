from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal
from models import ChatRecord
from services.rag_service import search_similar
from services.llm_service import ask_llm_stream, compress_history
from services.prompts import RAG_PROMPT, RAG_SYSTEM_PROMPT
from services.auth_service import require_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatMessage(BaseModel):
    role: str
    content: str


class RAGRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None


def build_history_with_summary(history: List[ChatMessage]) -> List[dict]:
    """构建带摘要的历史记录"""
    if not history:
        return []

    history_dicts = [{"role": msg.role, "content": msg.content} for msg in history]

    if len(history_dicts) <= 5:
        return history_dicts

    old_history = history_dicts[:-5]
    recent_history = history_dicts[-5:]

    summary = compress_history(old_history)

    result = []
    if summary:
        result.append({"role": "user", "content": f"[历史摘要] 之前我们讨论了：{summary}"})
        result.append({"role": "assistant", "content": "好的，我了解之前的对话内容。"})
    result.extend(recent_history)

    return result


@router.post("/rag/chat")
def rag_chat(request: RAGRequest, user_id: int = Depends(require_user)):
    """RAG 问答接口"""
    # 构建带摘要的历史
    history = build_history_with_summary(request.history)

    # 第1步：检索相关片段（只查当前用户的知识库）
    chunks = search_similar(request.question, top_k=3, user_id=user_id)

    if not chunks:
        return {"answer": "没有找到相关资料，请先上传文档。"}

    # 第2步：拼接 Prompt
    context = "\n\n".join(c["content"] for c in chunks)
    prompt = RAG_PROMPT.format(context=context, question=request.question)

    # 第3步：流式调用大模型
    def generate():
        # 先发送引用片段
        import json
        refs = json.dumps({"type": "references", "chunks": chunks}, ensure_ascii=False)
        yield f"data: {refs}\n\n"

        full_answer = ""
        try:
            for chunk in ask_llm_stream(prompt, history=history, system_prompt=RAG_SYSTEM_PROMPT):
                full_answer += chunk
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: 错误: {str(e)}\n\n"
        finally:
            if full_answer:
                try:
                    db = SessionLocal()
                    record = ChatRecord(user_id=user_id, question=request.question, answer=full_answer)
                    db.add(record)
                    db.commit()
                    db.close()
                except Exception:
                    pass
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/rag/chunks")
def get_chunks(user_id: int = Depends(require_user)):
    """查看当前用户向量库中的所有文档片段"""
    from services.rag_service import collection
    data = collection.get(where={"user_id": user_id})
    ids = data["ids"]
    docs = data["documents"]
    metas = data["metadatas"]
    return {
        "total": len(ids),
        "chunks": [
            {
                "id": ids[i],
                "content": docs[i][:200] + "..." if len(docs[i]) > 200 else docs[i],
                "filename": (metas[i] or {}).get("filename", "") if i < len(metas) else "",
            }
            for i in range(len(ids))
        ]
    }
