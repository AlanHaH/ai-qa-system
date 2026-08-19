import os
import requests
from datetime import datetime
from langchain_core.tools import tool

TAVILY_API_URL = "https://api.tavily.com/search"
DEFAULT_MAX_RESULTS = 5


class WebSearchError(Exception):
    pass


def _search(query: str) -> str:
    """调用 Tavily API 并格式化为纯文本。失败抛 WebSearchError。"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise WebSearchError("未配置 TAVILY_API_KEY")

    try:
        resp = requests.post(
            TAVILY_API_URL,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": DEFAULT_MAX_RESULTS,
                "include_answer": True,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise WebSearchError(f"Tavily 请求失败: {e}") from e

    results = data.get("results") or []
    if not results:
        return "没有搜索到与问题相关的信息。"

    lines = []
    if data.get("answer"):
        lines.append(f"Tavily 摘要：{data['answer']}")
    for i, item in enumerate(results[:DEFAULT_MAX_RESULTS], 1):
        title = item.get("title", "")
        url = item.get("url", "")
        content = (item.get("content") or "").strip()[:500]
        lines.append(f"[{i}] {title}\n来源：{url}\n内容：{content}")
    return "\n\n".join(lines)


@tool
def web_search(query: str) -> str:
    """联网搜索获取最新信息。当问题涉及实时新闻、最新动态、特定领域外部资料，或需要引用来源链接时，调用本工具。
    参数 query 是搜索关键词，尽量简洁并覆盖要点。"""
    return _search(query)


def run_web_search_tool_call(tool_call: dict) -> str:
    """执行模型返回的 web_search 工具调用，返回 ToolMessage 的内容。失败抛 WebSearchError。"""
    args = tool_call.get("args") or {}
    query = args.get("query")
    if not query:
        raise WebSearchError("工具调用缺少 query 参数")
    return _search(query)


def _format_now() -> str:
    """返回格式化的当前时间字符串"""
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    return f"当前时间：{now:%Y年%m月%d日} {now:%H:%M:%S} 星期{weekdays[now.weekday()]}"


@tool
def current_time() -> str:
    """获取当前日期和时间。当用户询问现在几点、今天是几号/星期几等时间相关问题时，调用本工具获取准确时间。"""
    return _format_now()


def run_current_time_tool_call(tool_call: dict) -> str:
    """执行 current_time 工具调用。"""
    return _format_now()
