# Day 07 复盘记录

## 今日目标

项目整体测试、写 README 文档、实现用户登录注册功能。

---

## 一、完成的事情

### 1. 项目整体测试

测试了所有后端接口，确认功能正常：

| 接口 | 状态 |
|------|------|
| GET `/` | ✅ 健康检查 |
| POST `/chat/stream` | ✅ 流式问答 |
| GET `/chat/history` | ✅ 聊天历史 |
| POST `/doc/upload` | ✅ 文档上传 |
| GET `/doc/list` | ✅ 文档列表 |
| DELETE `/doc/{id}` | ✅ 删除文档 |
| POST `/rag/chat` | ✅ RAG 问答 |
| GET `/rag/chunks` | ✅ 向量库数据 |
| POST `/user/register` | ✅ 用户注册 |
| POST `/user/login` | ✅ 用户登录 |

---

### 2. 写 README.md

**目的**：GitHub 上的项目介绍文档，让别人快速了解你的项目。

**包含内容**：
- 项目简介
- 技术栈表格
- 功能列表（已完成 / 待完成）
- 项目结构树
- 快速启动方法
- 接口文档表格
- RAG 流程图
- 后续计划

**写法要点**：
- 用 Markdown 语法，GitHub 会自动渲染
- 用表格展示接口，清晰明了
- 用代码块展示命令，方便复制
- 用勾选框 `[x]` 展示完成功能

---

### 3. 更新 requirements.txt

**为什么更新**：之前手动写的依赖不全，用 `pip freeze` 重新生成。

```powershell
pip freeze > requirements.txt
```

**作用**：别人克隆项目后，可以用 `pip install -r requirements.txt` 一键安装所有依赖。

---

### 4. 创建 .env.example

**为什么需要**：`.env` 包含密钥，不能提交到 Git。但别人需要知道需要配置哪些环境变量。

**`.env.example` 内容**：
```
# 大模型 API 配置
API_KEY=你的API密钥
BASE_URL=https://api.xiaomimimo.com/v1
MODEL_NAME=mimo-v2.5-pro
```

**用法**：别人克隆项目后，复制 `.env.example` 为 `.env`，填入自己的密钥。

---

### 5. 更新 .gitignore

**新增排除项**：
```
backend/chroma_db/  # 向量库数据（可重新生成）
```

**为什么要排除**：
- `chroma_db/` 是向量库数据文件，上传文档后会自动生成
- 每个人的向量库数据不同，不需要同步
- 文件可能很大，提交到 Git 会浪费空间

---

### 6. 用户登录注册功能

#### 6.1 安装依赖

```powershell
pip install python-jose[cryptography] passlib[bcrypt]
```

- `python-jose` — 生成和验证 JWT token
- `passlib` — 密码加密（后来发现和新版 bcrypt 不兼容，改用 bcrypt 直接调用）

#### 6.2 创建用户表

**`models.py` 新增**：
```python
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密后）")
    created_at = Column(DateTime, server_default=func.now(), comment="注册时间")
```

**关键字段**：
- `username` — `unique=True` 表示用户名不能重复
- `password` — 长度 255，因为加密后的密码很长

**创建表命令**：
```powershell
python -c "from database import engine, Base; import models; Base.metadata.create_all(engine); print('done')"
```

#### 6.3 创建认证服务

**`services/auth_service.py`**：

```python
import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时


def hash_password(password: str) -> str:
    """把明文密码加密成 bcrypt 哈希"""
    # bcrypt 需要 bytes 类型，所以 encode()
    # gensalt() 生成随机盐
    # hashpw() 加密
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码：明文密码 vs 加密后的密码"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """生成 JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解析 JWT token，返回 payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**密码加密详解**：

```
明文密码 "123456"
    ↓ bcrypt.hashpw()
加密后 "$2b$12$VNsXWBQWbvIGVgMQ08NE4e..."

为什么安全：
- 不可逆：加密后无法反推出明文
- 加盐：每次加密结果不同，即使密码相同
- 慢速：故意设计得很慢，防止暴力破解

验证过程：
verify_password("123456", "$2b$12$VNsXWBQWbvIGVgMQ08NE4e...") → True
verify_password("wrong", "$2b$12$VNsXWBQWbvIGVgMQ08NE4e...") → False
```

**JWT token 详解**：

```
JWT 由三部分组成，用 . 分隔：
Header.Payload.Signature

例如：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ6aGFuZ3NhbiIsImV4cCI6MTcyMDAwMDAwMH0.xxxxx

Header（头部）：算法信息
Payload（载荷）：用户信息 + 过期时间
Signature（签名）：验证 token 是否被篡改

生成过程：
data = {"sub": "zhangsan", "exp": 过期时间}
token = jwt.encode(data, SECRET_KEY, algorithm="HS256")

验证过程：
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
# 如果 token 有效，返回 {"sub": "zhangsan", "exp": ...}
# 如果 token 过期或被篡改，抛出 JWTError
```

#### 6.4 创建用户路由

**`routers/user.py`**：

```python
@router.post("/user/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        return {"error": "用户名已存在"}

    # 创建新用户（密码加密后存储）
    user = User(
        username=request.username,
        password=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "注册成功", "user_id": user.id}


@router.post("/user/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "用户名或密码错误"}

    # 验证密码
    if not verify_password(request.password, user.password):
        return {"error": "用户名或密码错误"}

    # 生成 JWT token
    token = create_access_token({"sub": user.username})

    return {
        "message": "登录成功",
        "token": token,
        "user_id": user.id,
        "username": user.username
    }
```

**注册流程**：
```
用户提交：username="zhangsan", password="123456"
    ↓
检查用户名是否已存在
    ↓
hash_password("123456") → "$2b$12$VNsXWBQWbvIGVgMQ08NE4e..."
    ↓
存入数据库：User(username="zhangsan", password="$2b$12$VNsXWBQWbvIGVgMQ08NE4e...")
```

**登录流程**：
```
用户提交：username="zhangsan", password="123456"
    ↓
查找用户
    ↓
verify_password("123456", "$2b$12$VNsXWBQWbvIGVgMQ08NE4e...") → True
    ↓
create_access_token({"sub": "zhangsan"}) → "eyJhbGciOi..."
    ↓
返回 token 给前端
```

---

### 7. 前端登录页面

**`views/Login.vue`**：

**核心功能**：
- 登录/注册表单切换
- 表单验证
- 登录成功保存 token 到 localStorage
- 注册成功自动切换到登录

**localStorage 详解**：
```javascript
// 浏览器本地存储，关闭页面数据还在
localStorage.setItem('token', 'eyJhbGciOi...')   // 保存
localStorage.getItem('token')                      // 读取 → 'eyJhbGciOi...'
localStorage.removeItem('token')                   // 删除

// 用途：保存登录状态
// 登录后保存 token，下次打开页面还在
// 退出时删除 token
```

**登录成功流程**：
```javascript
// 登录成功后
localStorage.setItem('token', data.token)       // 保存 token
localStorage.setItem('username', data.username)  // 保存用户名
localStorage.setItem('user_id', data.user_id)   // 保存用户 ID
router.push('/')                                  // 跳转到首页
```

---

### 8. 路由守卫

**`router/index.js`**：

```javascript
// 给需要登录的页面加标记
const routes = [
  { path: '/', component: Chat, meta: { requiresAuth: true } },
  { path: '/docs', component: Docs, meta: { requiresAuth: true } },
  { path: '/vectordb', component: VectorDB, meta: { requiresAuth: true } },
  { path: '/login', component: Login }
]

// 路由守卫：每次跳转前检查
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 如果访问需要登录的页面，但没有 token，跳转到登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})
```

**`beforeEach` 详解**：
- `to` — 要去的页面（包含 path、meta 等信息）
- `from` — 从哪来的页面
- `next()` — 放行，继续跳转
- `next('/login')` — 强制跳转到登录页

**执行流程**：
```
用户点击 "聊天" 链接
    ↓
router.beforeEach 自动执行
    ↓
检查 to.meta.requiresAuth（true）
    ↓
检查 localStorage.getItem('token')
    ↓
有 token → next() 放行
没有 token → next('/login') 跳转登录页
```

---

### 9. 导航栏用户状态

**`App.vue`**：

```vue
<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const username = ref(localStorage.getItem('username') || '')

// 监听路由变化，每次跳转页面时重新读取 localStorage
watch(() => route.path, () => {
  username.value = localStorage.getItem('username') || ''
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('user_id')
  username.value = ''
  router.push('/login')
}
</script>

<template>
  <nav>
    <div class="nav-left">
      <router-link to="/">聊天</router-link>
      <router-link to="/docs">知识库</router-link>
      <router-link to="/vectordb">向量库</router-link>
    </div>
    <div class="nav-right">
      <span v-if="username">
        {{ username }}
        <a @click="logout">退出</a>
      </span>
      <router-link v-else to="/login">登录</router-link>
    </div>
  </nav>
  <router-view />
</template>
```

**`watch` 详解**：
```javascript
// 监听某个值的变化，变化时执行回调
watch(() => route.path, () => {
  // route.path 变化时执行
  username.value = localStorage.getItem('username') || ''
})

// 为什么需要 watch？
// localStorage 不是响应式的，值变了页面不会自动更新
// 但 route.path 是响应式的，每次跳转页面都会变
// 所以监听 route.path，顺便更新 username
```

---

### 10. 向量库同步删除

**问题**：删除文档时，只删了 MySQL 里的记录，向量库里的片段没删。

**解决**：在 `rag_service.py` 新增删除函数：

```python
def delete_document(doc_id: int):
    """
    从向量库删除指定文档的所有片段。
    先查找该文档的所有 chunk ID，然后批量删除。
    """
    # 获取所有数据
    data = collection.get()
    # 找出以 doc_{doc_id}_ 开头的 ID
    ids_to_delete = [id for id in data["ids"] if id.startswith(f"doc_{doc_id}_")]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
```

**在 `doc.py` 调用**：
```python
@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    """删除指定文档"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "文档不存在"}

    # 同步删除向量库中的数据
    delete_document(doc_id)

    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}
```

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| `passlib` 和 `bcrypt` 不兼容 | 新版 bcrypt 改了接口 | 改用 `bcrypt` 直接调用 |
| `Table 'ai_qa.user' doesn't exist` | 忘记创建用户表 | 执行 `Base.metadata.create_all(engine)` |
| `win is not defined` | App.vue 写成了 `win` | 改成 `window` |
| 登录后导航栏不更新 | localStorage 不是响应式 | 用 `watch` 监听路由变化 |
| 向量库刷新按钮没反应 | 后端报错（向量库刚清空） | 重启后端 |
| 导入路径不一致 | `@/views/Login.vue` 和 `../views/xxx.vue` 混用 | 统一用相对路径 |

---

## 三、核心概念复习

### 什么是 JWT？

JSON Web Token，一种无状态的身份验证方式。

**组成**：`Header.Payload.Signature`

**工作流程**：
```
1. 用户登录，服务器验证密码
2. 服务器生成 JWT token，返回给前端
3. 前端保存 token 到 localStorage
4. 后续请求带上 token（Authorization: Bearer token）
5. 服务器解析 token，确认用户身份
```

**优点**：
- 无状态：服务器不需要保存 session
- 跨域：可以跨服务器验证
- 安全：签名防篡改

### 什么是 bcrypt？

一种密码哈希算法，专门用来加密密码。

**特点**：
- 不可逆：加密后无法反推
- 加盐：每次加密结果不同
- 慢速：故意设计慢，防暴力破解

### 什么是 localStorage？

浏览器本地存储，关闭页面数据还在。

**常用方法**：
```javascript
localStorage.setItem('key', 'value')  // 保存
localStorage.getItem('key')            // 读取
localStorage.removeItem('key')         // 删除
localStorage.clear()                   // 清空所有
```

### 什么是路由守卫？

在页面跳转前执行的检查函数，可以用来做权限控制。

```javascript
router.beforeEach((to, from, next) => {
  // to — 要去的页面
  // from — 从哪来的
  // next() — 放行
  // next('/login') — 跳转到登录页
})
```

---

## 四、当前后端接口汇总

| 方法 | 路径 | 功能 | 需要登录 |
|------|------|------|----------|
| GET | `/` | 健康检查 | 否 |
| POST | `/chat` | 普通问答 | 是 |
| POST | `/chat/stream` | 流式问答 | 是 |
| GET | `/chat/history` | 查询聊天历史 | 是 |
| POST | `/doc/upload` | 上传文档 | 是 |
| GET | `/doc/list` | 查询文档列表 | 是 |
| DELETE | `/doc/{id}` | 删除文档 | 是 |
| POST | `/rag/chat` | RAG 知识库问答 | 是 |
| GET | `/rag/chunks` | 查看向量库数据 | 是 |
| POST | `/user/register` | 用户注册 | 否 |
| POST | `/user/login` | 用户登录 | 否 |

---

## 五、当前项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # 入口，挂载路由
│   ├── database.py          # 数据库连接配置
│   ├── models.py            # 数据表模型（ChatRecord, Document, User）
│   ├── .env                 # API_KEY、BASE_URL、MODEL_NAME
│   ├── .env.example         # 环境变量模板
│   ├── chroma_db/           # ChromaDB 向量库数据
│   ├── routers/
│   │   ├── chat.py          # 聊天相关接口
│   │   ├── doc.py           # 文档相关接口
│   │   ├── rag.py           # RAG 问答接口
│   │   └── user.py          # 用户相关接口
│   └── services/
│       ├── llm_service.py   # 大模型调用（普通 + 流式）
│       ├── doc_service.py   # 文档文本提取
│       ├── rag_service.py   # RAG 服务（切分、向量库、检索）
│       └── auth_service.py  # 认证服务（密码加密、JWT）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 根组件（导航栏 + 路由出口）
│   │   ├── main.js          # 入口（挂载路由）
│   │   ├── router/
│   │   │   └── index.js     # 路由配置（含路由守卫）
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面
│   │       ├── Docs.vue     # 知识库管理页面
│   │       ├── VectorDB.vue # 向量库可视化页面
│   │       └── Login.vue    # 登录注册页面
│   └── package.json
├── README.md                # 项目文档
└── 复盘/
    ├── Day03复盘.md
    ├── Day04复盘.md
    ├── Day05复盘.md
    ├── Day06复盘.md
    ├── Day07复盘.md
    ├── Git使用指南.md
    └── 向量数据库详解.md
```

---

## 六、启动命令

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

## 七、用户数据隔离（重要修复）

### 问题发现

登录后，聊天记录和文档应该是**每个用户独立的**，而不是公共的。但测试发现：
1. 登录后对话保存不了
2. 退出再登录，历史记录清空了

### 问题原因

**JWT token 的 `sub` 字段类型错误**：

```python
# 错误写法：sub 是整数
token = create_access_token({"sub": user.id})  # user.id 是 int

# 正确写法：sub 必须是字符串
token = create_access_token({"sub": str(user.id)})  # 转成 str
```

**为什么**：JWT 标准规定 `sub`（subject）必须是字符串。`python-jose` 库在解析时会报错：`Subject must be a string`。

### 修复过程

**第1步：数据库加 user_id 字段**

```sql
ALTER TABLE chat_record ADD COLUMN user_id INT NOT NULL DEFAULT 0;
ALTER TABLE document ADD COLUMN user_id INT NOT NULL DEFAULT 0;
```

**第2步：models.py 加字段**

```python
class ChatRecord(Base):
    __tablename__ = "chat_record"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, comment="用户ID")  # 新增
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, comment="用户ID")  # 新增
    filename = Column(String(255), nullable=False, comment="文件名")
    content = Column(LONGTEXT, nullable=False, comment="提取的文本内容")
    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")
```

**第3步：登录时保存用户 ID 到 token（字符串）**

```python
# user.py 登录接口
token = create_access_token({"sub": str(user.id)})  # 转成字符串
```

**第4步：解析时转回整数**

```python
# auth_service.py
def get_current_user_id(token: str) -> int:
    """从 token 中获取当前用户 ID"""
    payload = decode_access_token(token)
    if not payload:
        return None
    # sub 是字符串，转成整数
    try:
        return int(payload.get("sub"))
    except (ValueError, TypeError):
        return None
```

**第5步：后端接口根据 user_id 过滤数据**

```python
# chat.py — 获取当前用户 ID
def get_user_id(authorization: str = Header(None)):
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    return get_current_user_id(token)

# chat_history — 只返回当前用户的记录
@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    if not user_id:
        return []
    records = db.query(ChatRecord).filter(
        ChatRecord.user_id == user_id  # 按用户过滤
    ).order_by(ChatRecord.id.desc()).limit(20).all()
    return [...]
```

**第6步：前端请求带上 token**

```javascript
// Chat.vue
function getHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  }
}

// 请求时带上 headers
const res = await fetch('http://127.0.0.1:8000/chat/history', {
  headers: getHeaders()
})
```

**第7步：流式接口数据库会话问题**

```python
# 问题：流式输出时，数据库会话在 AI 生成完之前就关闭了
# 解决：在 generate() 函数里创建新的数据库会话

def generate():
    full_answer = ""
    try:
        for chunk in ask_llm_stream(request.question):
            full_answer += chunk
            yield f"data: {chunk}\n\n"
    except Exception as e:
        yield f"data: 错误: {str(e)}\n\n"
    finally:
        # 流结束后保存到数据库（创建新会话）
        if full_answer:
            try:
                db = SessionLocal()  # 新建会话
                record = ChatRecord(user_id=user_id or 0, question=request.question, answer=full_answer)
                db.add(record)
                db.commit()
                db.close()
            except Exception:
                pass  # 保存失败不影响用户体验
    yield "data: [DONE]\n\n"
```

### 完整流程图

```
用户注册
    ↓
密码加密（bcrypt）→ 存入数据库
    ↓
用户登录
    ↓
验证密码 → 生成 JWT token（sub = 用户ID字符串）
    ↓
前端保存 token 到 localStorage
    ↓
后续请求带上 Authorization: Bearer token
    ↓
后端解析 token → 获取 user_id
    ↓
保存数据时带上 user_id
查询数据时按 user_id 过滤
    ↓
每个用户只能看到自己的数据
```

---

## 八、踩过的坑（补充）

| 坑 | 原因 | 解决方法 |
|---|---|---|
| JWT 解析失败 | `sub` 是整数，不是字符串 | 创建时 `str(user.id)`，解析时 `int(payload.get("sub"))` |
| 流式输出保存失败 | 数据库会话在流式过程中关闭 | 在 `generate()` 里创建新会话 |
| `Subject must be a string` | JWT 标准要求 sub 是字符串 | 转成字符串存储 |

---

## 九、明天计划

- [ ] 前端 UI 美化
- [ ] 添加更多 RAG 优化（调整参数、多文档检索）
- [ ] 项目截图（用于 README）
- [ ] 准备面试讲解
