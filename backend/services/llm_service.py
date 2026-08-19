import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from services.prompts import SYSTEM_PROMPT, COMPRESS_PROMPT
from services.web_search_service import (
    web_search, run_web_search_tool_call,
    current_time, run_current_time_tool_call,
)


class LLMConfigError(Exception):
    pass


_MODEL = None


def _get_model() -> ChatOpenAI:
    """懒加载单例。缺配置时抛 LLMConfigError（由调用方转成友好文案）。"""
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name = os.getenv("MODEL_NAME")
    missing = [k for k, v in {
        "API_KEY": api_key, "BASE_URL": base_url, "MODEL_NAME": model_name,
    }.items() if not v]
    if missing:
        raise LLMConfigError(f"没有配置{','.join(missing)},检查.env文件")

    _MODEL = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=(base_url or "").rstrip("/"),  # 去掉尾部斜杠，避免 //chat/completions
        max_tokens=1024,
        temperature=0.7,
        timeout=60,
        max_retries=1,
        streaming=True,
    )
    return _MODEL


def _to_langchain_messages(history) -> list:
    """把 [{"role","content"}] 转成 LangChain 消息，兼容 user/assistant/system。"""
    out = []
    for msg in history or []:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            out.append(SystemMessage(content=content))
        elif role == "assistant":
            out.append(AIMessage(content=content))
        else:
            out.append(HumanMessage(content=content))
    return out


def _content_to_str(content) -> str:
    """content 可能是 str 或内容块列表，统一成 str。"""
    if isinstance(content, list):
        return "".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def ask_llm(question: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """
    调用大模型，传入用户问题，返回大模型回答。
    """
    try:
        model = _get_model()
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
        return _content_to_str(model.invoke(messages).content)
    except LLMConfigError as e:
        return str(e)
    except Exception as e:
        return f"调用大模型失败:{str(e)}"


def _build_base_messages(question: str, history: list = None, system_prompt: str = SYSTEM_PROMPT) -> list:
    """普通问答的基础消息列表：System + 历史 + 当前问题。"""
    messages = [SystemMessage(content=system_prompt)]
    if history:
        messages.extend(_to_langchain_messages(history))
    messages.append(HumanMessage(content=question))
    return messages


def stream_messages(messages: list):
    """从预构建的 LangChain 消息列表流式输出纯文本。异常转成文本（不抛出）。"""
    try:
        model = _get_model()
        for chunk in model.stream(messages):
            text = _content_to_str(chunk.content)
            if text:
                yield text
    except LLMConfigError as e:
        yield str(e)
    except Exception as e:
        yield f"错误:{str(e)}"


def ask_llm_stream(question: str, history: list = None, system_prompt: str = SYSTEM_PROMPT):
    """
    流式调用大模型，支持历史记录。逐块 yield 纯文本。
    question: 当前问题
    history: 历史消息列表 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    messages = _build_base_messages(question, history, system_prompt)
    yield from stream_messages(messages)


def prepare_web_search(question: str, history: list = None, system_prompt: str = SYSTEM_PROMPT):
    """
    联网搜索的"工具决策 + 执行"阶段（非流式 invoke）。
    返回 (messages, tool_call, warning)：
      messages  — 最终流式回答要用的完整消息列表（命中工具则已追加 AIMessage(tool_calls) + ToolMessage）
      tool_call — 命中的工具调用 dict（含 id/name/args），未命中或失败为 None
      warning   — 降级提示文案，正常为 None
    本函数不抛异常：所有错误都转为 warning 并回退普通问答。
    """
    messages = _build_base_messages(question, history, system_prompt)

    # 阶段A：让模型决定是否调用工具（非流式，一次拿全 tool_calls）
    try:
        model = _get_model()
        model_with_tools = model.bind_tools([web_search, current_time])
        resp = model_with_tools.invoke(messages)
    except Exception as e:
        return messages, None, f"联网搜索功能暂不可用，已回退普通问答：{e}"

    tool_calls = getattr(resp, "tool_calls", None)
    if not tool_calls:
        return messages, None, None  # 模型决定不调用工具 → 直接普通回答

    supported = {"web_search", "current_time"}
    if any(tc.get("name") not in supported for tc in tool_calls):
        return messages, None, "模型请求了不支持的联网工具，已回退普通问答。"

    # 阶段B：按工具类型分发执行
    try:
        results = []
        for tc in tool_calls:
            name = tc.get("name")
            if name == "web_search":
                results.append(run_web_search_tool_call(tc))
            elif name == "current_time":
                results.append(run_current_time_tool_call(tc))
            else:
                raise ValueError(f"不支持的工具: {name}")
    except Exception as e:
        return messages, None, f"工具调用失败，已回退普通问答：{e}"

    # 按 OpenAI 工具调用规范：先一条 AIMessage(含全部 tool_calls)，再逐条 ToolMessage
    messages.append(AIMessage(content=resp.content or "", tool_calls=tool_calls))
    for tc, result in zip(tool_calls, results):
        messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

    return messages, tool_calls[0], None


def ask_llm_with_web_search(question: str, history: list = None, system_prompt: str = SYSTEM_PROMPT):
    """非流式联网问答，供 POST /chat 使用。返回 (answer, warning)。失败时 answer 为降级文案。"""
    try:
        messages, tool_call, warning = prepare_web_search(question, history, system_prompt)
        model = _get_model()
        answer = _content_to_str(model.invoke(messages).content)
        return answer, warning
    except Exception as e:
        return f"调用大模型失败:{str(e)}", None


def compress_history(history: list) -> str:
    """
    压缩历史记录为摘要。把旧对话交给大模型生成简短摘要。
    """
    if not history:
        return ""

    history_text = ""
    for msg in history:
        role = "用户" if msg.get("role") == "user" else "AI"
        history_text += f"{role}: {msg.get('content', '')[:200]}\n"

    try:
        model = _get_model()
        chain = COMPRESS_PROMPT | model | StrOutputParser()
        return chain.invoke({"history_text": history_text})
    except Exception:
        return ""
