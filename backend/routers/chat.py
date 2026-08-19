import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.llm_service import (
    ask_llm, ask_llm_stream, compress_history,
    prepare_web_search, stream_messages, ask_llm_with_web_search,
)
from services.prompts import WEB_SEARCH_SYSTEM_PROMPT
from services.auth_service import require_user

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None
    use_web_search: bool = False  # 是否开启联网搜索


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
def chat(request: ChatRequest, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    # 构建带摘要的历史
    history = build_history_with_summary(request.history)

    # 调用大模型（支持联网搜索）
    if request.use_web_search:
        answer, warning = ask_llm_with_web_search(request.question, history, WEB_SEARCH_SYSTEM_PROMPT)
        if warning:
            answer = f"[联网搜索提示] {warning}\n\n{answer}"
    else:
        answer = ask_llm(request.question)

    # 保存到数据库
    record = ChatRecord(user_id=user_id, question=request.question, answer=answer)
    db.add(record)
    db.commit()

    return {"question": request.question, "answer": answer}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, user_id: int = Depends(require_user)):
    """流式输出接口（支持联网搜索）"""
    # 构建带摘要的历史
    history = build_history_with_summary(request.history)

    def generate():
        full_answer = ""
        try:
            if request.use_web_search:
                # 阶段1：模型思考中
                yield f"data: {json.dumps({'type': 'web_search', 'phase': 'thinking'}, ensure_ascii=False)}\n\n"

                # 工具决策 + 执行（非流式）
                messages, tool_call, warning = prepare_web_search(
                    request.question, history, WEB_SEARCH_SYSTEM_PROMPT
                )

                # 阶段2：命中工具 → 通知"正在执行"
                if tool_call:
                    args = tool_call.get("args") or {}
                    query = args.get("query") if tool_call.get("name") == "web_search" else "获取当前时间"
                    yield f"data: {json.dumps({'type': 'web_search', 'phase': 'searching', 'query': query}, ensure_ascii=False)}\n\n"

                # 阶段3：降级提示
                if warning:
                    yield f"data: {json.dumps({'type': 'notice', 'message': warning}, ensure_ascii=False)}\n\n"

                # 阶段4：流式最终回答（用普通 model，不再触发工具）
                text_gen = stream_messages(messages)
            else:
                text_gen = ask_llm_stream(request.question, history=history)

            for chunk in text_gen:
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


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """查询当前用户的聊天记录"""
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
