# Day 06 复盘记录

## 今日目标

实现 RAG 核心功能：文本切分、向量化、相似度检索、RAG 问答。

---

## 一、完成的事情

### 1. 安装依赖

```powershell
pip install chromadb openai
```

- `chromadb` — 向量数据库，存储和检索向量
- `openai` — 调用 Embedding API（后来发现小米 API 没有 Embedding 模型，改用 ChromaDB 自带的）

---

### 2. 什么是向量数据库？

**普通数据库**（MySQL）：存的是结构化数据（文字、数字、日期）
```
| id | filename        | content     |
|----|-----------------|-------------|
| 1  | MySQL基础.pdf   | MySQL是...  |
```

**向量数据库**（ChromaDB）：存的是**向量**（一串浮点数）
```
| id           | document    | embedding              |
|--------------|-------------|------------------------|
| doc_1_chunk_0| MySQL是...  | [0.1, -0.3, 0.5, ...] |
| doc_1_chunk_1| 创建表...   | [0.2, -0.1, 0.4, ...] |
```

**向量是什么**：
- 向量就是一个浮点数数组，比如 `[0.1, -0.3, 0.5, 0.2, ...]`
- 它能表示文本的**语义**（意思）
- 相似意思的文本，向量也相似

**为什么需要向量数据库**：
```
用户问："MySQL 怎么建表？"

普通数据库：只能精确匹配关键词
  → 搜索 "MySQL 建表"，找不到就不返回

向量数据库：能理解语义
  → "MySQL 怎么建表" 和 "创建数据库表的方法" 意思相近
  → 向量相似度高，能检索到相关片段
```

**相似度计算**：
```
"MySQL 怎么建表"     → [0.1, -0.3, 0.5]
"创建数据库表的方法"  → [0.12, -0.28, 0.48]  ← 很相似！
"今天天气真好"       → [0.9, 0.1, -0.7]      ← 完全不相关
```

---

### 3. ChromaDB 详解

**初始化**：
```python
import chromadb

# 创建客户端，数据存在 chroma_db 目录
# PersistentClient — 持久化存储，重启后数据还在
chroma_client = chromadb.PersistentClient(path="chroma_db")

# 获取或创建一个集合（类似 MySQL 的"表"）
collection = chroma_client.get_or_create_collection(name="documents")
```

**添加数据**：
```python
collection.add(
    ids=["doc_1_chunk_0"],           # 唯一标识
    documents=["MySQL 是一个关系型数据库..."]  # 原始文本
)
# ChromaDB 会自动把文本转换成向量，不需要手动调 Embedding API
```

**查询数据**：
```python
results = collection.query(
    query_texts=["MySQL 怎么建表"],  # 用户的问题
    n_results=3                       # 返回最相似的前3个
)
# 返回：
# {
#   "documents": [["MySQL 创建表的语法...", "使用 CREATE TABLE..."]],
#   "distances": [[0.15, 0.23]]  ← 距离越小越相似
# }
```

**ChromaDB vs MySQL**：

| 对比项 | MySQL | ChromaDB |
|--------|-------|----------|
| 存什么 | 结构化数据（文字、数字） | 向量 + 原始文本 |
| 怎么查 | SQL 语句，精确匹配 | 语义相似度检索 |
| 适合场景 | 用户信息、订单、聊天记录 | 文档检索、问答系统 |
| 查询方式 | `SELECT * FROM users WHERE name='张三'` | `collection.query(query_texts=["张三是谁"])` |

---

### 4. 文本切分

**为什么要切分**：
- 大模型有 Token 限制（一次能处理的文本长度）
- 长文档不能一次性塞进 Prompt
- 需要把文档切成小块，只检索最相关的几块

**切分代码**：
```python
def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    把长文本切分成小块。
    chunk_size — 每块的最大字符数
    overlap — 相邻块重叠的字符数（保持上下文连贯）
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # 回退 overlap 个字符，保持连贯
    return chunks
```

**切分示例**：
```
原文本："ABCDEFGH"，chunk_size=4，overlap=1

第1块：ABCD
第2块：DEFG  ← 从 D 开始，和上一块重叠 1 个字符
第3块：GH

为什么要重叠？
→ 防止把一句话从中间切断，保持上下文连贯
```

**实际效果**：
```
原文本（1000字符）：
"MySQL 是一个关系型数据库管理系统。它使用 SQL 语言来管理数据。
创建表的语法是 CREATE TABLE。表由列组成，每列有数据类型..."

切分后：
chunk_0（500字符）："MySQL 是一个关系型数据库管理系统。它使用 SQL 语言来管理数据。创建表的语法是 CREATE TABLE..."
chunk_1（500字符）："创建表的语法是 CREATE TABLE。表由列组成，每列有数据类型..."
```

---

### 5. 存入向量库

**`services/rag_service.py`**：
```python
def add_document(doc_id: int, text: str):
    """
    把文档切分后存入向量库。
    doc_id — 文档 ID，用于关联数据库记录
    text — 文档的纯文本内容
    """
    chunks = split_text(text)  # 第1步：切分
    for i, chunk in enumerate(chunks):
        # 第2步：存入 ChromaDB（自动转向量）
        collection.add(
            ids=[f"doc_{doc_id}_chunk_{i}"],  # 唯一标识：doc_1_chunk_0
            documents=[chunk]                  # 原始文本
        )
```

**执行流程**：
```
上传 PDF
    ↓
提取文本（1000字符）
    ↓
切分成 2 块（chunk_0, chunk_1）
    ↓
存入 ChromaDB：
  - doc_1_chunk_0 → "MySQL 是一个..." → [0.1, -0.3, ...]
  - doc_1_chunk_1 → "创建表的语法..." → [0.2, -0.1, ...]
```

---

### 6. 相似度检索

**`services/rag_service.py`**：
```python
def search_similar(question: str, top_k: int = 3) -> list:
    """
    根据用户问题，从向量库检索最相关的文档片段。
    top_k — 返回最相似的前 k 个结果
    """
    results = collection.query(
        query_texts=[question],  # 用户的问题
        n_results=top_k          # 返回前3个
    )
    return results["documents"][0] if results["documents"] else []
```

**执行流程**：
```
用户问："MySQL 怎么建表？"
    ↓
ChromaDB 自动把问题转换成向量
    ↓
和向量库里所有向量计算相似度
    ↓
返回最相似的 3 个片段：
  1. "创建表的语法是 CREATE TABLE..."
  2. "表由列组成，每列有数据类型..."
  3. "MySQL 支持多种数据类型..."
```

---

### 7. RAG 问答接口

**`routers/rag.py`**：
```python
@router.post("/rag/chat")
def rag_chat(request: RAGRequest, db: Session = Depends(get_db)):
    """
    RAG 问答接口：
    1. 根据问题检索相关文档片段
    2. 把片段拼接成 Prompt
    3. 调用大模型生成回答
    """
    # 第1步：检索相关片段
    chunks = search_similar(request.question, top_k=3)

    if not chunks:
        return {"answer": "没有找到相关资料，请先上传文档。"}

    # 第2步：拼接 Prompt
    context = "\n\n".join(chunks)
    prompt = f"""请根据以下资料回答用户的问题。如果资料中没有相关内容，请说"资料中没有找到相关信息"。

相关资料：
{context}

用户问题：{request.question}"""

    # 第3步：流式调用大模型
    def generate():
        full_answer = ""
        for chunk in ask_llm_stream(prompt):
            full_answer += chunk
            yield f"data: {chunk}\n\n"
        # 保存到数据库
        record = ChatRecord(question=request.question, answer=full_answer)
        db.add(record)
        db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**RAG 的核心思想**：
```
普通问答：
  用户问题 → 大模型回答（靠自己的知识，可能有幻觉）

RAG 问答：
  用户问题 → 检索相关文档 → 拼接成 Prompt → 大模型基于资料回答（更准确）
```

**为什么 RAG 能减少幻觉**：
- 大模型的知识是训练时学到的，可能过时或不准确
- RAG 把真实资料塞进 Prompt，大模型"参考"资料回答
- 相当于开卷考试 vs 闭卷考试

---

### 8. 前端添加 RAG 开关

**`views/Chat.vue`**：
```vue
<template>
  <div class="input-area">
    <!-- 知识库问答开关 -->
    <label class="rag-toggle">
      <input type="checkbox" v-model="useRAG" />
      知识库问答
    </label>
    <input
      v-model="question"
      @keyup.enter="send"
      :placeholder="useRAG ? '基于知识库回答...' : '输入你的问题...'"
    />
    <button @click="send">发送</button>
  </div>
</template>

<script setup>
const useRAG = ref(false)  // 是否开启知识库问答

async function send() {
  // 根据开关选择接口
  const url = useRAG.value
    ? 'http://127.0.0.1:8000/rag/chat'      // RAG 问答
    : 'http://127.0.0.1:8000/chat/stream'   // 普通问答

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: q })
  })
  // ... 流式读取和显示
}
</script>
```

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| `openai.NotFoundError: 404` | 小米 API 没有 Embedding 模型 | 改用 ChromaDB 自带的 Embedding |
| `Data too long for column 'content'` | PDF 内容太长，Text 类型放不下 | 改用 LONGTEXT 类型 |
| `AttributeError: module 'routers.rag' has no attribute 'router'` | Python 缓存了旧文件 | 删除 `__pycache__` 目录 |

---

## 三、当前后端接口汇总

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/` | 健康检查 |
| POST | `/chat` | 普通问答（返回完整回答） |
| POST | `/chat/stream` | 流式问答（逐字返回） |
| GET | `/chat/history` | 查询聊天历史 |
| POST | `/doc/upload` | 上传文档 |
| GET | `/doc/list` | 查询文档列表 |
| DELETE | `/doc/{id}` | 删除文档 |
| POST | `/rag/chat` | RAG 知识库问答 |

---

## 四、RAG 完整流程图

```
【上传文档流程】
PDF/txt/md 文件
      ↓
extract_text() 提取纯文本
      ↓
save to MySQL（保存文件名和内容）
      ↓
split_text() 切分成小块（500字符，50重叠）
      ↓
add_document() 存入 ChromaDB 向量库
      ↓
ChromaDB 自动把每块文本转换成向量

【RAG 问答流程】
用户提问："MySQL 怎么建表？"
      ↓
search_similar() 从 ChromaDB 检索最相似的 3 个片段
      ↓
拼接 Prompt：
  "请根据以下资料回答...
   相关资料：
   片段1：创建表的语法是 CREATE TABLE...
   片段2：表由列组成...
   片段3：MySQL 支持多种数据类型...
   用户问题：MySQL 怎么建表？"
      ↓
ask_llm_stream() 调用大模型生成回答
      ↓
流式返回给前端，逐字显示
      ↓
保存到 MySQL 聊天记录
```

---

## 五、核心概念复习

### Embedding 是什么？
把文本转换成向量（浮点数数组）的过程。相似意思的文本，向量也相似。

```
"你好" → [0.1, -0.3, 0.5, 0.2]
"Hello" → [0.12, -0.28, 0.48, 0.22]  ← 很相似！
"今天天气" → [0.9, 0.1, -0.7, 0.3]   ← 完全不同
```

### 向量相似度怎么算？
常用**余弦相似度**（cosine similarity）：
- 值越接近 1，越相似
- 值越接近 0，越不相关

```
"MySQL 建表" 和 "创建数据库表" → 相似度 0.95
"MySQL 建表" 和 "今天吃什么"   → 相似度 0.12
```

### top_k 是什么？
返回最相似的前 k 个结果。k 越大，召回的内容越多，但可能有噪音；k 越小，越精准，但可能遗漏。

### overlap 的作用？
切分文本时，相邻块重叠一部分字符，防止把一句话从中间切断。

```
没有 overlap：
  块1："...创建表的"
  块2："语法是 CREATE TABLE..."
  → "创建表的" 和 "语法是" 被切断了

有 overlap：
  块1："...创建表的语法是"
  块2："语法是 CREATE TABLE..."
  → "语法是" 在两块中都有，上下文连贯
```

---

## 六、当前项目结构

```
pythonPJ/
├── backend/
│   ├── main.py              # 入口，挂载路由
│   ├── database.py          # 数据库连接配置
│   ├── models.py            # 数据表模型（ChatRecord, Document）
│   ├── .env                 # API_KEY、BASE_URL、MODEL_NAME
│   ├── chroma_db/           # ChromaDB 向量库数据（自动生成）
│   ├── routers/
│   │   ├── chat.py          # 聊天相关接口
│   │   ├── doc.py           # 文档相关接口
│   │   └── rag.py           # RAG 问答接口
│   └── services/
│       ├── llm_service.py   # 大模型调用（普通 + 流式）
│       ├── doc_service.py   # 文档文本提取
│       └── rag_service.py   # RAG 服务（切分、向量库、检索）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 根组件（导航栏 + 路由出口）
│   │   ├── main.js          # 入口（挂载路由）
│   │   ├── router/
│   │   │   └── index.js     # 路由配置
│   │   └── views/
│   │       ├── Chat.vue     # 聊天页面（普通 + RAG）
│   │       └── Docs.vue     # 知识库管理页面
│   └── package.json
└── 复盘/
    ├── Day03复盘.md
    ├── Day04复盘.md
    ├── Day05复盘.md
    ├── Day06复盘.md
    └── Git使用指南.md
```

---

## 七、启动命令

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

## 八、明天计划

- [ ] 优化 RAG 效果（调整 chunk_size、top_k 参数）
- [ ] 添加用户登录注册功能
- [ ] 前端 UI 美化
- [ ] 项目整体测试
