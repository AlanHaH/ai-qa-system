# Day 04 复盘记录

## 今日目标

搭建 Vue3 前端项目，实现聊天页面，前后端打通，实现流式输出。

---

## 一、完成的事情

### 1. 创建 Vue3 前端项目

**命令**：
```powershell
npm create vue@latest
```

**选项说明**：
| 选项 | 选什么 | 为什么 |
|---|---|---|
| Project name | frontend | 前端项目文件夹名 |
| TypeScript | No | 新手先不用 |
| JSX | No | Vue 默认用模板语法 |
| Vue Router | **Yes** | 页面跳转需要 |
| Pinia | No | 状态管理，现在用不上 |
| Vitest | No | 测试框架，现在用不上 |
| E2E Testing | No | 端到端测试，现在用不上 |
| ESLint | No | 代码风格检查，现在用不上 |

**安装额外依赖**：
```powershell
cd H:\pythonPJ\frontend
npm install vue-router@4 axios
```
- `vue-router@4` — Vue3 路由
- `axios` — HTTP 请求库（后来改用 fetch，但留着以后用）

### 2. 项目结构

```
frontend/src/
├── App.vue              # 根组件，只放 <router-view />
├── main.js              # 入口，挂载路由
├── router/
│   └── index.js         # 路由配置
└── views/
    └── Chat.vue         # 聊天页面
```

### 3. 路由配置

**`router/index.js`**：
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/Chat.vue'

const routes = [
  { path: '/', name: 'Chat', component: Chat }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**解释**：
- `createRouter` — 创建路由实例
- `createWebHistory` — 用浏览器 history 模式（URL 不带 `#`）
- `routes` — 定义路径和页面的对应关系

### 4. main.js 挂载路由

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
```

**关键**：`import router from './router'` 导入路由，`.use(router)` 启用路由。

**踩过的坑**：写成了 `import './router'`（没有赋值给变量），导致 `router` 未定义报错。

### 5. App.vue

```vue
<template>
  <router-view />
</template>
```

`<router-view />` 是路由的"出口"，路由匹配到哪个页面，就在这里显示。

### 6. 聊天页面 Chat.vue

**template 部分**（HTML）：
- `v-for` — 循环渲染每条消息
- `:class` — 用户消息靠右（蓝色），AI 消息靠左（灰色）
- `v-model` — 输入框和 `question` 变量双向绑定
- `@keyup.enter` — 按回车触发发送

**script 部分**（JS）：
- `ref` — Vue3 的响应式变量，值变了页面自动更新
- `fetch` — 发 HTTP 请求到后端接口
- `messages` — 存所有聊天记录的数组

**style 部分**（CSS）：
- 聊天气泡样式，用户蓝色靠右，AI 灰色靠左

### 7. 跨域问题（CORS）

**问题**：前端在 `localhost:5173`，后端在 `localhost:8000`，浏览器默认不允许跨端口请求。

**解决**：在后端 `main.py` 加 CORS 中间件：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有来源
    allow_methods=["*"],      # 允许所有请求方法
    allow_headers=["*"],      # 允许所有请求头
)
```

### 8. 流式输出

**为什么要流式输出**：普通接口要等 AI 生成完才返回，用户要等很久。流式输出让 AI 的回答逐字出现，体验更好。

**后端实现**：

**`services/llm_service.py` 新增 `ask_llm_stream` 函数**：
```python
def ask_llm_stream(question: str):
    # 关键：stream=True 开启流式
    data = {
        "model": MODEL_NAME,
        "messages": [...],
        "stream": True
    }
    response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)

    # 逐行读取 SSE 数据
    for line in response.iter_lines():
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        data_str = line[6:]  # 去掉 "data: " 前缀
        if data_str == "[DONE]":
            break
        chunk = json.loads(data_str)
        choices = chunk.get("choices", [])
        if not choices:
            continue
        delta = choices[0].get("delta", {})
        content = delta.get("content", "")
        if content:
            yield content  # 逐个返回文本片段
```

**`routers/chat.py` 新增流式接口**：
```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    def generate():
        full_answer = ""
        for chunk in ask_llm_stream(request.question):
            full_answer += chunk
            yield f"data: {chunk}\n\n"  # SSE 格式
        # 流结束后保存到数据库
        record = ChatRecord(question=request.question, answer=full_answer)
        db.add(record)
        db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**前端实现**：
```javascript
const res = await fetch('http://127.0.0.1:8000/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: q })
})

const reader = res.body.getReader()
const decoder = new TextDecoder()
let buffer = ''  // 缓存未处理完的数据

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  buffer += decoder.decode(value, { stream: true })
  const lines = buffer.split('\n')
  buffer = lines.pop()  // 最后一行可能不完整，留到下次处理

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const content = line.slice(6).trim()
      if (content === '[DONE]') return
      if (content) {
        messages.value[aiIndex].content += content
      }
    }
  }
}
```

**SSE 是什么**：Server-Sent Events，服务器向客户端推送数据的协议。格式是每行以 `data: ` 开头，以 `\n\n` 结尾。

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| `router is not defined` | `import './router'` 没赋值给变量 | 改成 `import router from './router'` |
| Network Error | 跨域问题，前后端端口不同 | 后端加 CORS 中间件 |
| `list index out of range` | 流式解析时 `choices` 数组为空 | 加 `if not choices: continue` 检查 |
| SSE 数据不完整 | 一个 chunk 可能包含多个或不完整的消息 | 用 `buffer` 缓存，按行分割处理 |

---

## 三、核心概念复习

### Vue3 的 ref 是什么？
响应式变量。`const question = ref('')` 创建一个变量，值变了页面自动更新。读取时用 `question.value`，模板里直接用 `question`。

### fetch 和 axios 的区别？
- `fetch` — 浏览器内置，不需要安装，支持流式读取
- `axios` — 需要安装，功能更丰富，但不支持流式读取

### SSE 和 WebSocket 的区别？
- SSE — 单向（服务器→客户端），基于 HTTP，适合流式输出
- WebSocket — 双向通信，适合实时聊天、游戏

### CORS 是什么？
Cross-Origin Resource Sharing，跨域资源共享。浏览器安全机制，不同端口/域名之间发请求需要服务器明确允许。

---

## 四、启动命令

```powershell
# 终端1 — 后端
cd H:\pythonPJ\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload

# 终端2 — 前端
cd H:\pythonPJ\ 
npm run dev
```

前端访问：http://localhost:5173

---

## 五、明天计划

- [ ] 实现聊天历史查询接口 GET /chat/history
- [ ] 前端添加聊天历史展示
- [ ] 优化 UI 样式
- [ ] 开始文档上传功能
