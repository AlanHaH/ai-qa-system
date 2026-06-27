# Day 05 复盘记录

## 今日目标

实现聊天历史查询 + 文档上传功能（知识库管理）

---

## 一、完成的事情

### 1. 聊天历史查询接口

**目的**：用户刷新页面后，之前的聊天记录不会丢失。

**后端代码 `routers/chat.py`**：
```python
@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db)):
    """查询最近20条聊天记录"""
    # .order_by(ChatRecord.id.desc()) 按 ID 倒序排列（最新在前）
    # .limit(20) 只取20条
    # .all() 返回所有结果
    records = db.query(ChatRecord).order_by(ChatRecord.id.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "created_at": str(r.created_at)
        }
        for r in records
    ]
```

**用法**：
- `GET /chat/history` — 返回最近20条记录
- 返回格式：`[{id, question, answer, created_at}, ...]`

**前端代码 `views/Chat.vue`**：
```javascript
// onMounted — Vue3 生命周期钩子，页面加载完成后自动执行
onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/chat/history')
    const data = await res.json()
    // 数据库返回的是倒序（最新在前），需要反转成正序
    data.reverse().forEach(record => {
      messages.value.push({ role: 'user', content: record.question })
      messages.value.push({ role: 'ai', content: record.answer })
    })
  } catch (err) {
    console.log('加载历史记录失败：', err)
  }
})
```

**用法**：
- `onMounted` — 页面加载时自动执行，不需要用户触发
- `data.reverse()` — 反转数组顺序，让旧的聊天记录显示在上面
- `forEach` — 遍历数组，把每条记录拆成"用户问题"和"AI回答"两条消息

**为什么不同接口返回同一页面**：
```
接口返回的是数据，不是页面
        ↓
前端 JavaScript 拿到数据
        ↓
把数据塞进 messages 数组
        ↓
Vue 自动渲染到页面上
```

一个页面可以调多个接口，每个接口负责不同的事：
- `/chat/stream` — 用户点发送时调用，发问题拿 AI 回答
- `/chat/history` — 页面加载时调用，拉历史记录

---

### 2. 安装依赖

```powershell
pip install python-multipart PyPDF2
```

- `python-multipart` — FastAPI 处理文件上传必须的库
- `PyPDF2` — 读取 PDF 文件内容的库

---

### 3. 文档数据表

**目的**：存储上传的文档信息和提取的文本内容。

**`models.py` 新增代码**：
```python
class Document(Base):
    __tablename__ = "document"  # 数据库里的表名

    # Column(类型, 约束条件, 注释)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Integer — 整数类型
    # primary_key=True — 主键（唯一标识每一行）
    # index=True — 建索引（查得快）
    # autoincrement=True — 自增（自动 +1）

    filename = Column(String(255), nullable=False, comment="文件名")
    # String(255) — 最长255个字符的字符串
    # nullable=False — 不允许为空

    content = Column(Text, nullable=False, comment="提取的文本内容")
    # Text — 长文本类型，不限长度，适合存文档内容

    created_at = Column(DateTime, server_default=func.now(), comment="上传时间")
    # DateTime — 时间类型
    # server_default=func.now() — 默认值是数据库当前时间（插入时自动填）
```

**创建表的命令**：
```powershell
python -c "from database import engine, Base; import models; Base.metadata.create_all(engine); print('done')"
```

**解释**：
- `from database import engine, Base` — 导入数据库连接和基类
- `import models` — 导入 models.py，让 Document 类注册到 Base 上
- `Base.metadata.create_all(engine)` — 把所有继承 Base 的表创建到数据库

---

### 4. 文档服务（文本提取）

**目的**：从上传的文件中提取纯文本内容。

**`services/doc_service.py`**：
```python
import PyPDF2
import io

def extract_text(file_content: bytes, filename: str) -> str:
    """
    从文件内容中提取文本。
    file_content — 文件的二进制内容（bytes 类型）
    filename — 文件名，用来判断文件类型
    """
    if filename.endswith(".pdf"):
        return extract_pdf(file_content)
        # 如果是 PDF，调用专门的 PDF 解析函数
    elif filename.endswith((".txt", ".md")):
        return file_content.decode("utf-8")
        # 如果是 txt 或 md，直接解码成字符串
        # decode("utf-8") 把二进制转换成字符串
    else:
        return "不支持的文件格式"


def extract_pdf(file_content: bytes) -> str:
    """从 PDF 中提取文本"""
    try:
        # io.BytesIO 把二进制数据包装成文件对象
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            # reader.pages 是所有页面的列表
            # page.extract_text() 提取当前页的文本
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"PDF解析失败: {str(e)}"
```

**用法**：
```python
# 读取上传的文件
content = await file.read()  # 得到二进制数据 (bytes)
text = extract_text(content, file.filename)  # 提取纯文本
```

**什么是 bytes 类型**：
- 文件在电脑上是以二进制（0和1）存储的
- 读取文件时得到的就是 bytes 类型
- `.decode("utf-8")` 把二进制转换成人能看懂的字符串

---

### 5. 文档路由

**目的**：提供上传、查询、删除文档的接口。

**`routers/doc.py`**：
```python
from fastapi import APIRouter, UploadFile, File, Depends
# APIRouter — 创建路由对象
# UploadFile — FastAPI 的文件上传类型
# File(...) — 标记这个参数是文件
# Depends — 依赖注入

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document
from services.doc_service import extract_text

router = APIRouter()

# 依赖注入：提供数据库会话（和 chat.py 里一样）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/doc/upload")
async def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传文档，提取文本并保存到数据库"""
    # file: UploadFile = File(...)
    # — file 是上传的文件对象
    # — File(...) 表示这是必填参数

    content = await file.read()
    # await — 等待异步操作完成
    # file.read() — 读取文件的二进制内容

    text = extract_text(content, file.filename)
    # 调用服务函数提取文本

    doc = Document(filename=file.filename, content=text)
    # 创建 Document 对象（相当于构造一条数据库记录）

    db.add(doc)
    # 把记录加入会话（还没真正写入数据库）

    db.commit()
    # 提交到数据库（这时候才真正写入）

    db.refresh(doc)
    # 刷新对象，获取数据库自动生成的字段（比如 id）

    return {
        "id": doc.id,
        "filename": doc.filename,
        "message": "上传成功"
    }


@router.get("/doc/list")
def doc_list(db: Session = Depends(get_db)):
    """查询所有文档列表"""
    docs = db.query(Document).order_by(Document.id.desc()).all()
    # db.query(Document) — 查询 Document 表
    # .order_by(Document.id.desc()) — 按 ID 倒序排列
    # .all() — 返回所有结果（列表）

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "created_at": str(d.created_at)
        }
        for d in docs
    ]
    # 列表推导式：遍历 docs，把每个 d 转换成字典


@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    """删除指定文档"""
    # {doc_id} 是路径参数，访问 /doc/3 时 doc_id=3
    # : int 表示必须是整数

    doc = db.query(Document).filter(Document.id == doc_id).first()
    # .filter(Document.id == doc_id) — 筛选条件：id 等于 doc_id
    # .first() — 只取第一条结果

    if not doc:
        return {"error": "文档不存在"}

    db.delete(doc)
    # 从数据库删除这条记录

    db.commit()
    return {"message": "删除成功"}
```

**用法**：
- `POST /doc/upload` — 上传文件（form-data 格式）
- `GET /doc/list` — 获取文档列表
- `DELETE /doc/3` — 删除 ID 为 3 的文档

---

### 6. 挂载文档路由

**`main.py`**：
```python
from routers import chat, doc  # 导入两个路由模块

# 分别挂载，不能同时传两个
app.include_router(chat.router)
app.include_router(doc.router)
```

**踩过的坑**：
```python
# 错误写法：include_router 只能一次传一个
app.include_router(chat.router, doc.router)

# 正确写法：分两次调用
app.include_router(chat.router)
app.include_router(doc.router)
```

---

### 7. 前端文档管理页面

**`views/Docs.vue`**：

**template 部分**：
```html
<!-- 文件选择框 -->
<input type="file" @change="handleFile" accept=".pdf,.txt,.md" />
<!-- type="file" — 文件选择框 -->
<!-- @change — 选择文件时触发 handleFile 函数 -->
<!-- accept=".pdf,.txt,.md" — 只允许选择这三种格式 -->

<!-- 上传按钮 -->
<button @click="upload" :disabled="!selectedFile">上传</button>
<!-- :disabled="!selectedFile" — 没选文件时按钮禁用 -->

<!-- 文档列表 -->
<div v-for="doc in docs" :key="doc.id" class="doc-item">
  <span class="doc-name">{{ doc.filename }}</span>
  <span class="doc-time">{{ doc.created_at }}</span>
  <button @click="remove(doc.id)">删除</button>
</div>
<!-- v-for="doc in docs" — 遍历 docs 数组，每个元素叫 doc -->
<!-- :key="doc.id" — 唯一标识，Vue 用来高效更新 DOM -->
```

**script 部分**：
```javascript
import { ref, onMounted } from 'vue'

const docs = ref([])           // 文档列表
const selectedFile = ref(null) // 选中的文件

// 加载文档列表
async function loadDocs() {
  const res = await fetch('http://127.0.0.1:8000/doc/list')
  docs.value = await res.json()
}

// 选择文件
function handleFile(e) {
  selectedFile.value = e.target.files[0]
  // e.target — 触发事件的元素（input）
  // e.target.files — 用户选中的文件列表
  // [0] — 取第一个文件
}

// 上传文件
async function upload() {
  if (!selectedFile.value) return

  const formData = new FormData()
  // FormData — 用来封装文件数据的容器
  // 文件上传必须用 FormData，不能用 JSON

  formData.append('file', selectedFile.value)
  // 'file' — 参数名，要和后端的参数名一致
  // selectedFile.value — 文件对象

  const res = await fetch('http://127.0.0.1:8000/doc/upload', {
    method: 'POST',
    body: formData
    // body 发送 FormData，浏览器会自动设置 Content-Type
  })
  const data = await res.json()
  alert(data.message)        // 弹出提示
  selectedFile.value = null  // 清空选中的文件
  loadDocs()                 // 刷新文档列表
}

// 删除文档
async function remove(id) {
  if (!confirm('确定删除？')) return
  // confirm() — 弹出确认框，用户点"确定"返回 true，点"取消"返回 false

  const res = await fetch(`http://127.0.0.1:8000/doc/${id}`, { method: 'DELETE' })
  const data = await res.json()
  alert(data.message)
  loadDocs()  // 刷新文档列表
}

// 页面加载时自动获取文档列表
onMounted(() => loadDocs())
```

---

### 8. 前端导航栏

**`App.vue`**：
```vue
<template>
  <nav>
    <router-link to="/">聊天</router-link>
    <router-link to="/docs">知识库</router-link>
  </nav>
  <router-view />
</template>
```

**解释**：
- `<router-link to="/">` — 点击跳转到 `/`，显示聊天页面
- `<router-link to="/docs">` — 点击跳转到 `/docs`，显示知识库页面
- `<router-view />` — 路由出口，匹配到哪个页面就显示哪个
- `router-link-active` — CSS 类名，当前页面的链接自动添加这个类

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| `NameError: name 'Depends' is not defined` | doc.py 漏了 Depends 导入 | 加上 `from fastapi import ..., Depends` |
| `include_router` 报错 | 同时传了两个路由 | 分成两行写 |
| `/upload` 404 | 路由路径少了 `/doc` 前缀 | 改成 `/doc/upload` |
| `Document(name=...)` 报错 | 字段名写错了 | 改成 `Document(filename=...)` |
| 列表返回用了花括号 | `{}` 是集合，`[]` 是列表 | 改成 `[{} for d in docs]` |

---

## 三、核心概念复习

### FormData 是什么？
用来封装文件数据的容器。文件上传不能用 JSON 格式，必须用 FormData。

```javascript
const formData = new FormData()
formData.append('file', fileObject)      // 添加文件
formData.append('name', 'test.txt')     // 也可以添加普通字段
```

### UploadFile 是什么？
FastAPI 提供的文件上传类型。常用属性：
- `file.filename` — 原始文件名
- `file.content_type` — 文件类型（如 application/pdf）
- `await file.read()` — 读取文件内容（二进制）

### bytes 和 string 的区别？
- `string` — 人能看懂的字符串，如 `"你好"`
- `bytes` — 二进制数据，如 `b'\xe4\xbd\xa0\xe5\xa5\xbd'`
- `encode()` — 字符串 → 二进制
- `decode()` — 二进制 → 字符串

### 列表推导式是什么？
```python
# 普通写法
result = []
for d in docs:
    result.append({"id": d.id, "filename": d.filename})

# 列表推导式（一行搞定）
result = [{"id": d.id, "filename": d.filename} for d in docs]
```

### 刷新列表的模式
```
上传/删除成功
      ↓
调用 loadDocs() 重新获取列表
      ↓
docs.value 被更新
      ↓
Vue 自动重新渲染页面
```

---

## 四、当前后端接口汇总

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/` | 健康检查 |
| POST | `/chat` | 普通问答（返回完整回答） |
| POST | `/chat/stream` | 流式问答（逐字返回） |
| GET | `/chat/history` | 查询聊天历史 |
| POST | `/doc/upload` | 上传文档 |
| GET | `/doc/list` | 查询文档列表 |
| DELETE | `/doc/{id}` | 删除文档 |

---

## 五、当前项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # 入口，挂载路由
│   ├── database.py          # 数据库连接配置
│   ├── models.py            # 数据表模型（ChatRecord, Document）
│   ├── .env                 # API_KEY、BASE_URL、MODEL_NAME
│   ├── routers/
│   │   ├── chat.py          # 聊天相关接口
│   │   └── doc.py           # 文档相关接口
│   └── services/
│       ├── llm_service.py   # 大模型调用（普通 + 流式）
│       └── doc_service.py   # 文档文本提取
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 根组件（导航栏 + 路由出口）
│   │   ├── main.js          # 入口（挂载路由）
│   │   ├── router/
│   │   │   └── index.js     # 路由配置
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面
│   │       └── Docs.vue     # 知识库管理页面
│   └── package.json
└── 复盘/
    ├── Day03复盘.md
    ├── Day04复盘.md
    └── Day05复盘.md
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

前端访问：http://localhost:5173

---

## 七、明天计划

- [ ] 开始 RAG 核心功能（文本切分、Embedding、向量库）
- [ ] 实现 RAG 问答接口
- [ ] 前端接入 RAG 问答
