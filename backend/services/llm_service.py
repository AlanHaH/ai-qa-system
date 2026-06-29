import os
import json
#导入请求包
import requests
#把main的service函数拆分到llm_service.py中
def ask_llm(question:str)->str:
    """
        调用大模型 API，传入用户问题，返回大模型回答。
    """
    #从.env文件中读取配置文件
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL_NAME=os.getenv("MODEL_NAME")

    if not API_KEY:
        return "没有配置API_KEY,检查.env文件"
    if not BASE_URL:
        return "没有配置BASE_URL,检查.env文件"
    if not MODEL_NAME:
        return "没有配置MODEL_NAME,检查.env文件"

    url = f"{BASE_URL}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
       "model": MODEL_NAME,
        "messages":[
            {
                "role":"system",
                "content":"你是一个学习助手，请用适合大学生理解的方式回答问题"
            },
            {
                "role":"user",
                "content":question
            }
        ],
        "max_completion_tokens": 1024,
    }

    try:
        response=requests.post(url,headers=headers,json=data,timeout=30)
       
        if response.status_code != 200:
            return f"大模型API请求失败,状态码:{response.status_code},返回内容为:{response.text}"
       
        result = response.json()
  
        if "choices" not in result:
            return f"大模型格式异常:{result}"
       
        answer = result["choices"][0]["message"]["content"]
    
        return answer
    except requests.exceptions.Timeout:
        return f"调用大模型超时,请稍后重试"
    except requests.exceptions.RequestException as e:
        return f"网络请求失败:{str(e)}"
    except Exception as e:
        return f"程序发生未知错误:{str(e)}"


def ask_llm_stream(question: str, history: list = None):
    """
    流式调用大模型 API，支持历史记录。
    question: 当前问题
    history: 历史消息列表 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")

    if not API_KEY or not BASE_URL or not MODEL_NAME:
        yield "配置错误，检查.env文件"
        return

    url = f"{BASE_URL}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构建消息列表
    messages = [
        {
            "role": "system",
            "content": "你是一个学习助手，请用适合大学生理解的方式回答问题"
        }
    ]

    # 添加历史记录
    if history:
        messages.extend(history)

    # 添加当前问题
    messages.append({
        "role": "user",
        "content": question
    })

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_completion_tokens": 1024,
        "stream": True
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)

        if response.status_code != 200:
            yield f"请求失败，状态码:{response.status_code}"
            return

        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

    except Exception as e:
        yield f"错误:{str(e)}"


def compress_history(history: list) -> str:
    """
    压缩历史记录为摘要。
    把旧的对话发送给 AI，让它生成简短摘要。
    """
    if not history:
        return ""

    # 构建压缩提示
    history_text = ""
    for msg in history:
        role = "用户" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content'][:200]}\n"

    prompt = f"""请用3-5句话概括以下对话的要点，保留关键信息：

{history_text}

要求：只输出摘要，不要加其他内容。"""

    # 调用 AI 生成摘要
    result = ask_llm(prompt)
    return result