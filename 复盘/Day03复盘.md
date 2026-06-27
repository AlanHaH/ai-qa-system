# Day 03 复盘记录

## 今日目标

完成第1周验收（大模型 API 调通）+ 后端目录拆分 + MySQL 数据库接入

---

## 一、完成的事情

### 1. 大模型 API 调通（第1周验收）

**遇到的问题**：POST /chat 返回 401 Unauthorized

**排查过程**：
1. 最初是 `Authorization` 请求头缺少 `Bearer ` 前缀
2. 加上 `Bearer ` 后仍然 401，发现是 `Bearer` 和 key 之间**少了空格**
3. 修复后仍然 401，发现端口 8000 上有**多个旧的 uvicorn 进程**，新服务器没生效
4. 杀掉所有旧进程后重启，API 调用成功

**学到的教训**：
- 401 = 认证失败，先检查 API Key 和请求头格式
- 改了代码没生效 → 先用 `netstat -ano | grep ":8000"` 检查端口占用
- 有多个进程就 `taskkill //F //IM uvicorn.exe` 全部杀掉再启动

### 2. 后端目录拆分

**原来**：所有代码写在一个 `main.py` 里

**拆分后**：
```
backend/
├── main.py              # 入口，只负责启动和挂载路由
├── routers/
│   └── chat.py          # 路由定义（@router.post）
├── services/
│   └── llm_service.py   # 业务逻辑（ask_llm()）
├── database.py          # 数据库连接配置
├── models.py            # 数据表模型
└── .env                 # 环境变量
```

**学到的知识**：
- `routers/` 放路由（接口定义），`services/` 放业务逻辑（具体干活的函数）
- `APIRouter()` 创建路由对象，`@router.post("/chat")` 定义接口
- `app.include_router(chat.router)` 把路由挂载到主应用上
- `FastAPI()` 是创建应用，`APIRouter()` 是创建路由，不能混用

### 3. MySQL 数据库接入

**安装依赖**：
- `sqlalchemy` — ORM 框架，用 Python 代码操作数据库，不用写 SQL
- `pymysql` — MySQL 驱动，让 Python 能连接 MySQL

**创建的文件**：

#### `database.py` — 数据库连接配置
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:密码@localhost:3306/ai_qa"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**逐行解释**：
- `create_engine(DATABASE_URL)` — 创建数据库连接引擎
- `sessionmaker(...)` — 创建会话工厂，用来生成数据库会话
- `declarative_base()` — 创建基类，所有表模型都继承它

#### `models.py` — 数据表模型
```python
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class ChatRecord(Base):
    __tablename__ = "chat_record"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=False, comment="AI回答")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
```

**逐行解释**：
- `Column` — 表示表里的一列
- `Integer` — 整数类型
- `Text` — 长文本类型（不限长度）
- `DateTime` — 时间类型
- `primary_key=True` — 主键（唯一标识每一行）
- `autoincrement=True` — 自增（自动 +1）
- `nullable=False` — 不允许为空
- `server_default=func.now()` — 默认值是数据库当前时间

**创建表的命令**：
```python
from database import engine, Base
import models  # 导入 models 让 ChatRecord 注册到 Base 上
Base.metadata.create_all(engine)
```

#### `routers/chat.py` — 保存聊天记录
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ChatRecord
from services.llm_service import ask_llm

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer = ask_llm(request.question)

    # 保存到数据库
    record = ChatRecord(question=request.question, answer=answer)
    db.add(record)
    db.commit()

    return {"question": request.question, "answer": answer}
```

**学到的知识**：
- **依赖注入**：`Depends(get_db)` 让 FastAPI 自动调用 `get_db()`，不用手动写
- **yield**：`get_db()` 用 `yield db` 把会话交给路由函数，用完后自动关闭
- **保存记录三步**：创建对象 → `db.add()` → `db.commit()`

---

## 二、踩过的坑

| 坑 | 原因 | 解决方法 |
|---|---|---|
| 401 Unauthorized | `Bearer` 和 key 之间少了空格 | 加上空格 `Bearer {key}` |
| 改了代码没生效 | 端口上有多个旧进程 | `taskkill //F //IM uvicorn.exe` 全杀掉 |
| `cannot import name 'Base' from 'models'` | Base 不是 models.py 定义的 | 改成 `from database import engine, Base; import models` |
| `'FastAPI' object has no attribute '_contains_router'` | `router = FastAPI()` 写错了 | 改成 `router = APIRouter()` |
| pip 装到全局了 | 没激活 venv 就 pip install | 先 `.\venv\Scripts\Activate.ps1` 再装 |

---

## 三、核心概念复习

### SQLAlchemy 是什么？
ORM 框架，把数据库表映射成 Python 类。用 Python 代码操作数据库，不用写 SQL。

### APIRouter 是什么？
路由对象，用来组织接口。把路由从 main.py 拆分到独立文件，main.py 只负责挂载。

### Depends 是什么？
FastAPI 的依赖注入机制。`Depends(get_db)` 表示"调用这个路由前，先调用 get_db()，把结果传给参数 db"。

### yield 是什么？
生成器关键字。`get_db()` 用 `yield db` 暂停函数，把 db 交给调用者用，用完后继续执行 `finally: db.close()`。

---

## 四、今日验证命令

```bash
# 启动服务器
cd H:\pythonPJ\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload

# 测试接口
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"question\":\"hello\"}"

# 查看数据库记录
# 在 MySQL 中执行：
USE ai_qa;
SELECT * FROM chat_record;
```

---

## 五、深入理解：Python 怎么连接数据库？

### 没有 SQLAlchemy 的话，要自己写 SQL 连接代码

```python
import pymysql

# 1. 建立连接
conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="123456",
    database="ai_qa"
)

# 2. 创建游标（执行 SQL 的工具）
cursor = conn.cursor()

# 3. 执行 SQL
cursor.execute(
    "INSERT INTO chat_record (question, answer) VALUES (%s, %s)",
    ("你好", "hello")
)

# 4. 提交
conn.commit()

# 5. 关闭
cursor.close()
conn.close()
```

每次操作数据库都要写这么多重复代码，很麻烦。

### 有了 SQLAlchemy，封装好了

```python
from database import SessionLocal
from models import ChatRecord

db = SessionLocal()                              # 相当于 conn + cursor
record = ChatRecord(question="你好", answer="hello")  # 相当于构造 SQL
db.add(record)                                   # 相当于 cursor.execute(...)
db.commit()                                      # 相当于 conn.commit()
db.close()                                       # 相当于 conn.close()
```

### database.py 里每个变量对应什么

```
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/ai_qa"
                  ↑         ↑      ↑         ↑       ↑
               MySQL驱动  用户名  密码      地址    数据库名

engine = create_engine(DATABASE_URL)      # 创建连接池（管理多个连接）
SessionLocal = sessionmaker(bind=engine)  # 会话工厂，调用一次就生成一个会话
Base = declarative_base()                 # 表模型的基类
```

---

## 六、深入理解：怎么自动保存到数据库？

### 关键：依赖注入

```python
# 第1步：定义一个"提供数据库会话"的函数
def get_db():
    db = SessionLocal()    # 创建会话（打开连接）
    try:
        yield db           # 把会话"借"给路由函数用
    finally:
        db.close()         # 用完后自动关闭

# 第2步：路由函数通过 Depends(get_db) 自动拿到 db
@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    answer = ask_llm(request.question)

    # 第3步：用 db 保存记录
    record = ChatRecord(question=request.question, answer=answer)
    db.add(record)     # 把记录加入会话
    db.commit()        # 提交到数据库

    return {"question": request.question, "answer": answer}
```

### 执行流程

```
用户发请求 POST /chat
        ↓
FastAPI 看到 db: Session = Depends(get_db)
        ↓
自动调用 get_db()，拿到 db（数据库会话）
        ↓
执行 ask_llm(question)，拿到 AI 回答
        ↓
创建 ChatRecord 对象
        ↓
db.add(record) → 把记录加入会话
        ↓
db.commit() → 提交到 MySQL
        ↓
返回回答给用户
        ↓
get_db() 的 finally 执行，db.close() 自动关闭连接
```

### yield 的作用

```python
def get_db():
    db = SessionLocal()    # 1. 创建会话
    try:
        yield db           # 2. 暂停，把 db 交给路由函数用
    finally:
        db.close()         # 4. 路由函数用完了，自动关闭
```

就像借东西：`yield db` 是"把 db 借给你"，`finally: db.close()` 是"你用完了我收回来"。

---

## 七、深入理解：`def chat(request: ChatRequest, db: Session = Depends(get_db))` 语法

```python
def chat(request: ChatRequest, db: Session = Depends(get_db)):
```

逐个拆解：

### 1. `def chat(...)` — 定义函数

### 2. `request: ChatRequest`
- `request` — 参数名
- `: ChatRequest` — 类型注解，表示这个参数必须是 `ChatRequest` 类型
- FastAPI 会自动把请求体的 JSON 解析成 `ChatRequest` 对象

### 3. `db: Session = Depends(get_db)`
- `db` — 参数名
- `: Session` — 类型注解，表示这是 SQLAlchemy 的会话对象
- `= Depends(get_db)` — 默认值，意思是"不要用户传，FastAPI 自动调用 `get_db()` 来生成"

### 4. `Depends(get_db)`
- `Depends` 是 FastAPI 提供的函数
- `get_db` 是你写的函数（**不加括号**，传的是函数本身，不是调用结果）
- FastAPI 收到请求时，会自动调用 `get_db()`，把 `yield` 出来的 `db` 传给路由函数

### 等价的写法（没有 Depends）

```python
# 有 Depends（简洁）
@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    ...

# 没有 Depends（手动调用）
@router.post("/chat")
def chat(request: ChatRequest):
    db = SessionLocal()
    try:
        ...  # 业务逻辑
        db.commit()
    finally:
        db.close()
```

`Depends` 就是帮你省掉了手动创建和关闭会话的代码。

---

## 八、明天计划

- [ ] 实现聊天历史查询接口 GET /chat/history
- [ ] 开始搭建 Vue3 前端项目
- [ ] 实现简单聊天页面
