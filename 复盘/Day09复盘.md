# Day 09 复盘记录

## 今日目标

实现对话记忆功能（历史记录压缩），让 AI 记住之前的对话内容。

---

## 一、完成的事情

### 1. 对话记忆功能

**问题**：之前每次提问都是独立的，AI 不记得之前的对话。

```
没有记忆：
  用户："什么是 Python？"
  AI："Python 是一种编程语言..."
  用户："它有什么优点？"  ← AI 不知道"它"指什么
```

**解决方案**：把最近的聊天记录一起发给大模型，作为上下文。

```
有记忆：
  用户："什么是 Python？"
  AI："Python 是一种编程语言..."
  用户："它有什么优点？"
  发送给 AI 的消息：
    - user: "什么是 Python？"
    - assistant: "Python 是一种编程语言..."
    - user: "它有什么优点？"  ← AI 知道"它"指 Python
```

---

### 2. 历史记录压缩

**问题**：如果把所有历史都发给 AI，token 会超限。

**解决方案**：
- 最近 5 条：完整保留
- 超过 5 条：旧的压缩成摘要

```
完整历史（20条）
    ↓
拆分：
  - 最近5条：完整保留
  - 之前15条：压缩成摘要
    ↓
发送给 AI：
  - system: "你是一个学习助手"
  - user: "[历史摘要] 用户之前问了 Python 基础、for 循环..."
  - assistant: "了解，之前讨论了 Python 基础知识..."
  - 最近5条对话
  - user: 当前问题
```

---

### 3. 后端实现

#### 3.1 LLM 服务支持历史记录

**`services/llm_service.py`**：

```python
def ask_llm_stream(question: str, history: list = None):
    """
    流式调用大模型 API，支持历史记录。
    question: 当前问题
    history: 历史消息列表
    """
    # 构建消息列表
    messages = [
        {"role": "system", "content": "你是一个学习助手..."}
    ]

    # 添加历史记录
    if history:
        messages.extend(history)

    # 添加当前问题
    messages.append({"role": "user", "content": question})

    # 调用 API
    data = {"model": MODEL_NAME, "messages": messages, ...}
```

#### 3.2 历史压缩函数

**`services/llm_service.py`**：

```python
def compress_history(history: list) -> str:
    """
    压缩历史记录为摘要。
    把旧的对话发送给 AI，让它生成简短摘要。
    """
    # 构建压缩提示
    history_text = ""
    for msg in history:
        role = "用户" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content'][:200]}\n"

    prompt = f"请用3-5句话概括以下对话的要点：\n{history_text}"

    # 调用 AI 生成摘要
    result = ask_llm(prompt)
    return result
```

#### 3.3 聊天接口支持历史记录

**`routers/chat.py`**：

```python
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = None


def build_history_with_summary(history: List[ChatMessage]) -> List[dict]:
    """
    构建带摘要的历史记录。
    如果历史超过5条，旧的压缩成摘要，最近5条保留。
    """
    if not history:
        return []

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
        result.append({"role": "user", "content": f"[历史摘要] 之前我们讨论了：{summary}"})
        result.append({"role": "assistant", "content": "好的，我了解之前的对话内容。"})
    result.extend(recent_history)

    return result
```

---

### 4. 前端实现

**`views/Chat.vue`**：

```javascript
async function send() {
  // ...

  // 构建历史记录（最近10条）
  const history = messages.value
    .slice(0, -1)  // 排除当前空的 AI 消息
    .filter(msg => msg.content)  // 过滤空内容
    .slice(-10)  // 只取最近10条
    .map(msg => ({
      role: msg.role === 'ai' ? 'assistant' : msg.role,
      content: msg.content
    }))

  const res = await fetch(url, {
    method: 'POST',
    headers: { ... },
    body: JSON.stringify({ question: q, history: history })
  })
}
```

---

### 5. 完整流程

```
用户提问："它有什么优点？"
    ↓
前端构建 history：
  [
    {"role": "user", "content": "什么是 Python？"},
    {"role": "assistant", "content": "Python 是一种编程语言..."}
  ]
    ↓
发送给后端：{question: "它有什么优点？", history: [...]}
    ↓
后端 build_history_with_summary()：
  history <= 5条？直接返回
  history > 5条？压缩旧历史 + 保留最近5条
    ↓
压缩旧历史：调用 AI 生成摘要
    ↓
构建最终 messages：
  [
    {"role": "system", "content": "你是一个学习助手..."},
    {"role": "user", "content": "[历史摘要] 之前讨论了 Python 基础..."},
    {"role": "assistant", "content": "好的，我了解..."},
    {"role": "user", "content": "什么是 Python？"},
    {"role": "assistant", "content": "Python 是一种编程语言..."},
    {"role": "user", "content": "它有什么优点？"}
  ]
    ↓
发送给大模型 API
    ↓
返回回答："Python 的优点有..."
```

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| AI 不记得之前的对话 | 没有发送历史记录 | 前端发送 history，后端拼接到 messages |
| token 超限 | 历史记录太多 | 只保留最近5条，旧的压缩成摘要 |
| 压缩摘要太慢 | 每次都要调用 AI | 只在历史超过5条时才压缩 |

---

## 三、核心概念复习

### 什么是对话记忆？

让 AI 记住之前的对话内容，实现多轮对话。

### 为什么需要压缩？

大模型有 token 限制（一次能处理的文本长度）。如果历史记录太多，会超过限制。

### 压缩原理

```
旧历史（15条）
    ↓
发送给 AI："请概括以下对话要点..."
    ↓
AI 返回摘要："用户问了 Python 基础、for 循环、列表操作..."
    ↓
摘要（1条）+ 最近5条 = 6条
    ↓
发送给 AI 生成回答
```

### 前端发送历史的逻辑

```javascript
const history = messages.value
  .slice(0, -1)        // 排除当前空的 AI 消息
  .filter(msg => msg.content)  // 过滤空内容
  .slice(-10)          // 只取最近10条
  .map(msg => ({
    role: msg.role === 'ai' ? 'assistant' : msg.role,
    content: msg.content
  }))
```

---

## 四、当前后端接口汇总

| 方法 | 路径 | 功能 | 需要登录 |
|------|------|------|----------|
| GET | `/` | 健康检查 | 否 |
| POST | `/chat` | 普通问答（支持历史） | 是 |
| POST | `/chat/stream` | 流式问答（支持历史） | 是 |
| GET | `/chat/history` | 查询聊天历史 | 是 |
| POST | `/doc/upload` | 上传文档 | 是 |
| GET | `/doc/list` | 查询文档列表 | 是 |
| DELETE | `/doc/{id}` | 删除文档 | 是 |
| POST | `/rag/chat` | RAG 问答（支持历史） | 是 |
| GET | `/rag/chunks` | 查看向量库数据 | 是 |
| POST | `/user/register` | 用户注册 | 否 |
| POST | `/user/login` | 用户登录 | 否 |
| GET | `/user/me` | 获取当前用户信息 | 是 |

---

## 五、启动命令

```powershell
# 终端1 — 后端
cd H:\pythonPJ\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload

# 终端2 — 前端
cd H:\pythonPJ\frontend
npm run dev
```

---

## 六、剩余任务

| 项目 | 状态 |
|------|------|
| 项目截图 | ❌ |
| 简历项目描述 | ❌ |
| 2 分钟项目讲解稿 | ❌ |
| 准备 30 个面试问题 | ❌ |
| Agent 工具调用 | ❌（可选） |
