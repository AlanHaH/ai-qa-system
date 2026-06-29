# Day 08 复盘记录

## 今日目标

补全技术栈（Element Plus、Axios、Pinia）、添加引用片段功能、UI 美化。

---

## 一、完成的事情

### 1. Element Plus 集成

**安装**：
```powershell
npm install element-plus
```

**配置 `main.js`**：
```javascript
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

createApp(App).use(router).use(ElementPlus).mount('#app')
```

**用到的组件**：
| 组件 | 用途 | 使用页面 |
|------|------|----------|
| `<el-input>` | 输入框 | Chat、Login |
| `<el-button>` | 按钮 | 所有页面 |
| `<el-checkbox>` | 复选框 | Chat |
| `<el-upload>` | 文件上传 | Docs |
| `<el-tag>` | 标签 | Docs、VectorDB |
| `<el-empty>` | 空状态 | Docs、VectorDB |
| `<el-alert>` | 提示框 | Login |
| `ElMessage` | 消息提示 | Docs、Login |
| `ElMessageBox` | 弹窗确认 | Docs |

---

### 2. Axios 集成

**安装**：
```powershell
npm install axios
```

**创建 `api.js`**：
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000
})

// 请求拦截器：自动带上 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

**用法**：
```javascript
import api from '../api'

// GET 请求
const res = await api.get('/chat/history')
console.log(res.data)

// POST 请求
const res = await api.post('/user/login', { username: 'test', password: '123456' })

// DELETE 请求
const res = await api.delete('/doc/1')

// 上传文件（单独设置超时）
const res = await api.post('/doc/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  timeout: 120000
})
```

**Axios vs Fetch**：
| 对比项 | Axios | Fetch |
|--------|-------|-------|
| 自动转 JSON | ✅ `res.data` | ❌ 需要 `res.json()` |
| 请求拦截器 | ✅ | ❌ |
| 超时设置 | ✅ `timeout` | ❌ 需要自己实现 |
| 错误处理 | ✅ 自动抛出异常 | ❌ 需要检查 `res.ok` |
| 流式响应 | ❌ 不支持 | ✅ 支持 |

**为什么流式响应用 Fetch**：Axios 不支持 `ReadableStream`，流式响应必须用 Fetch。

---

### 3. Pinia 集成

**安装**：
```powershell
npm install pinia
```

**配置 `main.js`**：
```javascript
import { createPinia } from 'pinia'
const pinia = createPinia()
createApp(App).use(pinia)...
```

**创建 `stores/user.js`**：
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(localStorage.getItem('user_id') || '')

  // 登录
  function login(tokenVal, usernameVal, userIdVal) {
    token.value = tokenVal
    username.value = usernameVal
    userId.value = userIdVal
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('username', usernameVal)
    localStorage.setItem('user_id', userIdVal)
  }

  // 退出
  function logout() {
    token.value = ''
    username.value = ''
    userId.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('user_id')
  }

  // 是否已登录
  const isLoggedIn = () => !!token.value

  // 获取当前用户信息
  async function fetchUserInfo() {
    if (!token.value) return null
    try {
      const res = await api.get('/user/me')
      if (res.data.user_id) {
        username.value = res.data.username
        userId.value = res.data.user_id
        localStorage.setItem('username', res.data.username)
        localStorage.setItem('user_id', res.data.user_id)
        return res.data
      }
      return null
    } catch {
      return null
    }
  }

  return { token, username, userId, login, logout, isLoggedIn, fetchUserInfo }
})
```

**用法**：
```javascript
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

// 读取状态
console.log(userStore.username)

// 调用方法
userStore.login('token', 'zhangsan', 1)
userStore.logout()

// 异步方法
await userStore.fetchUserInfo()
```

**Pinia vs localStorage**：
| 对比项 | Pinia | localStorage |
|--------|-------|--------------|
| 响应式 | ✅ 页面自动更新 | ❌ 需要手动刷新 |
| 方法封装 | ✅ login/logout | ❌ 每次自己写 |
| 跨组件共享 | ✅ | ✅ |
| 持久化 | ❌ 刷新丢失 | ✅ |

**为什么两者都用**：Pinia 提供响应式和方法封装，localStorage 提供持久化。登录时同时写入两者。

---

### 4. RAG 引用片段

**后端实现**：
```python
# rag.py
def generate():
    # 先发送引用片段（JSON 格式）
    refs = json.dumps({"type": "references", "chunks": chunks}, ensure_ascii=False)
    yield f"data: {refs}\n\n"

    # 再发送 AI 回答
    for chunk in ask_llm_stream(prompt):
        yield f"data: {chunk}\n\n"

    yield "data: [DONE]\n\n"
```

**前端解析**：
```javascript
for (const line of lines) {
  if (line.startsWith('data: ')) {
    const content = line.slice(6).trim()
    if (content === '[DONE]') return

    // 检查是否是引用片段
    try {
      const data = JSON.parse(content)
      if (data.type === 'references') {
        messages.value[aiIndex].refs = data.chunks
        messages.value[aiIndex].showRefs = true
        continue
      }
    } catch {
      // 不是 JSON，正常文本
    }

    // 普通文本
    messages.value[aiIndex].content += content
  }
}
```

**前端渲染**：
```html
<div v-if="msg.refs && msg.refs.length > 0" class="references">
  <div class="refs-header" @click="msg.showRefs = !msg.showRefs">
    📚 引用了 {{ msg.refs.length }} 个文档片段
    <span class="toggle-icon">{{ msg.showRefs ? '▼' : '▶' }}</span>
  </div>
  <div v-show="msg.showRefs" class="refs-list">
    <div v-for="(ref, i) in msg.refs" :key="i" class="ref-item">
      <span class="ref-index">#{{ i + 1 }}</span>
      <span class="ref-content">{{ ref }}</span>
    </div>
  </div>
</div>
```

**完整流程**：
```
用户提问
    ↓
POST /rag/chat
    ↓
search_similar() 检索相关片段
    ↓
SSE 流式响应：
  data: {"type":"references","chunks":["片段1","片段2","片段3"]}
  data: MySQL 创建表的语法是...
  data: 使用 CREATE TABLE 语句...
  data: [DONE]
    ↓
前端解析：
  - JSON 格式 → 保存到 msg.refs
  - 普通文本 → 追加到 msg.content
    ↓
页面渲染：
  - 可折叠的引用区域
  - AI 回答
```

---

### 5. 获取当前用户信息

**后端接口**：`GET /user/me`

**前端实现**：
```javascript
// stores/user.js
async function fetchUserInfo() {
  if (!token.value) return null
  try {
    const res = await api.get('/user/me')
    if (res.data.user_id) {
      username.value = res.data.username
      userId.value = res.data.user_id
      localStorage.setItem('username', res.data.username)
      localStorage.setItem('user_id', res.data.user_id)
      return res.data
    }
    return null
  } catch {
    return null
  }
}

// App.vue
onMounted(async () => {
  if (userStore.isLoggedIn()) {
    await userStore.fetchUserInfo()
  }
})
```

**作用**：页面加载时自动获取最新用户信息，保持状态同步。

---

### 6. UI 美化

**登录页面**：
- 深色渐变背景（深蓝紫）
- 动态光效动画
- 毛玻璃表单
- 渐变按钮 + hover 上浮动画

**聊天页面**：
- 欢迎消息
- 头像（用户 👤、AI 🤖）
- 自动滚动到底部
- 引用片段折叠区域

**知识库页面**：
- 虚线上传区域
- 文件图标
- 空状态提示
- loading 效果

**向量库页面**：
- 统计卡片（渐变背景）
- 片段序号标签
- 空状态提示

**导航栏**：
- Logo
- 左右布局
- 用户名显示
- 退出按钮

---

### 7. 上传 Loading 效果

```vue
<el-button type="primary" @click="upload" :disabled="!selectedFile" :loading="uploading">
  {{ uploading ? '上传中...' : (selectedFile ? '上传 ' + selectedFile.name : '上传') }}
</el-button>
```

```javascript
const uploading = ref(false)

async function upload() {
  uploading.value = true
  try {
    // 上传逻辑
  } finally {
    uploading.value = false
  }
}
```

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| `api.js` 导出失败 | 文件内容被覆盖 | 重新写入文件 |
| `baseURL` 写错 | 写成了 8080 | 改成 8000 |
| 上传超时 | 默认 30 秒太短 | 单独设置 120 秒 |
| `alert()` 太丑 | 浏览器自带弹窗 | 换成 `ElMessage` |

---

## 三、技术栈完成情况

| 技术 | 状态 | 说明 |
|------|------|------|
| Vue3 | ✅ | 前端框架 |
| Vue Router | ✅ | 页面路由 |
| Element Plus | ✅ | UI 组件库 |
| Axios | ✅ | HTTP 请求库 |
| Pinia | ✅ | 状态管理 |
| Python | ✅ | 后端语言 |
| FastAPI | ✅ | Web 框架 |
| Uvicorn | ✅ | ASGI 服务器 |
| Requests | ✅ | HTTP 客户端 |
| python-dotenv | ✅ | 环境变量 |
| MySQL | ✅ | 关系型数据库 |
| SQLAlchemy | ✅ | ORM 框架 |
| ChromaDB | ✅ | 向量数据库 |
| JWT | ✅ | 身份认证 |
| bcrypt | ✅ | 密码加密 |

---

## 四、当前项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # 入口
│   ├── database.py          # 数据库连接
│   ├── models.py            # 数据表模型
│   ├── .env                 # 环境变量
│   ├── routers/
│   │   ├── chat.py          # 聊天接口
│   │   ├── doc.py           # 文档接口
│   │   ├── rag.py           # RAG 接口
│   │   └── user.py          # 用户接口
│   └── services/
│       ├── llm_service.py   # 大模型调用
│       ├── doc_service.py   # 文档处理
│       ├── rag_service.py   # RAG 服务
│       └── auth_service.py  # 认证服务
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # 入口
│   │   ├── api.js           # Axios 实例
│   │   ├── router/
│   │   │   └── index.js     # 路由配置
│   │   ├── stores/
│   │   │   └── user.js      # 用户状态
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面
│   │       ├── Docs.vue     # 知识库页面
│   │       ├── VectorDB.vue # 向量库页面
│   │       └── Login.vue    # 登录页面
│   └── package.json
├── README.md
└── 复盘/
```

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
