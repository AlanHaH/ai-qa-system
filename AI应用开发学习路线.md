AI应用开发实习学习计划 Markdown 清单
目标：8月初开始投递杭州 AI应用开发 / 大模型应用开发 / Python后端 / RAG / Agent 应用相关实习岗位。

当前主线项目：基于大模型与 RAG 的学习资料智能问答系统

核心原则：先做出能运行、能演示、能写进简历的项目，再逐步优化。

一、最终目标
[ ] 8月初开始投递实习岗位
[ ] 完成一个 AI 应用开发项目
[ ] 项目可以本地运行
[ ] 项目有 GitHub 仓库
[ ] 项目有 README 文档
[ ] 项目有截图或演示说明
[ ] 简历中能清楚写出项目经历
[ ] 面试时能讲清楚项目架构、RAG 流程、大模型 API 调用流程
二、目标岗位关键词
优先投递：

[ ] 杭州 AI应用开发实习生
[ ] 杭州 大模型应用开发实习生
[ ] 杭州 Python后端实习生
[ ] 杭州 AIGC应用开发实习生
[ ] 杭州 RAG实习生
[ ] 杭州 Agent开发实习生
[ ] 杭州 AI产品研发实习生
[ ] 杭州 后端开发实习生 大模型方向
[ ] 杭州 LLM应用开发实习生
暂时不优先投递：

[ ] 大模型算法工程师
[ ] 深度学习算法实习生
[ ] NLP算法实习生
[ ] 多模态算法实习生
[ ] 模型训练工程师
原因：这些岗位通常更偏硕士、算法、模型训练和论文能力，本科阶段先主攻 AI 应用落地方向更现实。

三、项目名称
[ ] 项目名：基于大模型与 RAG 的学习资料智能问答系统
项目一句话介绍：

用户上传学习资料后，系统对文档进行文本提取、切分、向量化和检索，用户提问时，系统先检索相关资料片段，再调用大模型生成更贴合资料内容的回答。

四、项目技术栈 前端
[ ] Vue3
[ ] Element Plus
[ ] Axios
[ ] Vue Router
[ ] Pinia
后端
[ ] Python
[ ] FastAPI
[ ] Uvicorn
[ ] Requests
[ ] python-dotenv
数据库
[ ] MySQL
[ ] SQLAlchemy
AI 与 RAG
[ ] 大模型 API：DeepSeek / OpenAI / 通义千问任选一个
[ ] Prompt 模板
[ ] Embedding
[ ] 文本切分 Chunk
[ ] 向量数据库 Chroma 或 FAISS
[ ] 相似度检索
[ ] RAG 检索增强生成
五、项目最终功能清单 用户模块
[ ] 用户注册
[ ] 用户登录
[ ] Token 认证
[ ] 获取当前用户信息
聊天模块
[ ] 普通 AI 问答
[ ] RAG 知识库问答
[ ] 聊天记录保存
[ ] 聊天历史查询
文档模块
[ ] 上传 PDF 文件
[ ] 上传 txt 文件
[ ] 上传 md 文件
[ ] 文档列表展示
[ ] 删除文档
[ ] 文档文本提取
[ ] 文本切分
[ ] 文本向量化
[ ] 存入向量库
RAG 模块
[ ] 根据用户问题生成查询向量
[ ] 从向量库检索相关 chunk
[ ] 拼接 Prompt
[ ] 调用大模型生成回答
[ ] 返回引用片段
前端模块
[ ] 登录页面
[ ] 注册页面
[ ] 聊天页面
[ ] 知识库管理页面
[ ] 文件上传组件
[ ] 聊天历史展示
[ ] Loading 状态
[ ] 错误提示
六、6周总学习计划 第1周：Python 后端 + 大模型 API
目标：跑通 FastAPI 后端，并成功调用大模型 API。

[ ] 复习 Python 基础：函数、字典、列表、异常处理
[ ] 学习 FastAPI 基础：GET、POST、请求体、返回 JSON
[ ] 创建 backend 项目目录
[ ] 创建 Python 虚拟环境 venv
[ ] 安装 fastapi、uvicorn、requests、python-dotenv
[ ] 编写 main.py
[ ] 实现 GET / 测试接口
[ ] 实现 POST /chat 测试接口
[ ] 创建 .env 文件
[ ] 配置 API_KEY、BASE_URL、MODEL_NAME
[ ] 封装 ask_llm(question) 函数
[ ] 使用 requests 调用大模型 API
[ ] 在 /docs 中测试普通 AI 问答
验收标准：

[ ] http://127.0.0.1:8000 可以访问
[ ] http://127.0.0.1:8000/docs 可以访问
[ ] POST /chat 可以返回真实 AI 回答
第2周：Vue3 前端 + 聊天页面
目标：做出简单聊天页面，并打通前后端。

[ ] 创建 frontend 项目
[ ] 安装 Vue3
[ ] 安装 Element Plus
[ ] 安装 Axios
[ ] 创建 Chat.vue 页面
[ ] 创建输入框和发送按钮
[ ] 使用 Axios 请求后端 /chat 接口
[ ] 展示用户问题
[ ] 展示 AI 回答
[ ] 添加 loading 状态
[ ] 添加错误提示
验收标准：

[ ] 前端可以输入问题
[ ] 点击发送后请求 FastAPI
[ ] 页面可以展示 AI 回答
第3周：RAG 知识库核心功能
目标：让 AI 根据上传资料回答问题。

[ ] 理解 RAG 流程
[ ] 实现 PDF / txt / md 文本读取
[ ] 实现 extract_text(file_path)
[ ] 实现 split_text(text, chunk_size=500, overlap=50)
[ ] 学习 Embedding 基本概念
[ ] 封装 get_embedding(text)
[ ] 接入 Chroma 或 FAISS
[ ] 实现 save_chunks_to_vector_db()
[ ] 实现 search_similar_chunks()
[ ] 实现 POST /chat/rag 接口
[ ] 将检索结果拼接进 Prompt
[ ] 返回 RAG 回答和引用片段
验收标准：

[ ] 上传一份学习资料
[ ] 用户提问时可以检索相关片段
[ ] 大模型能结合资料回答
第4周：数据库 + 工程化
目标：把 Demo 变成完整项目结构。

[ ] 安装 SQLAlchemy
[ ] 配置 MySQL 连接
[ ] 创建 database.py
[ ] 创建 config.py
[ ] 创建 user 表
[ ] 创建 document 表
[ ] 创建 chat_record 表
[ ] 实现注册接口 POST /user/register
[ ] 实现登录接口 POST /user/login
[ ] 实现获取当前用户 GET /user/me
[ ] 实现聊天记录保存
[ ] 实现聊天历史查询 GET /chat/history
[ ] 整理 routers 目录
[ ] 整理 services 目录
[ ] 整理 models 目录
[ ] 整理 schemas 目录
验收标准：

[ ] 用户可以注册登录
[ ] 聊天记录可以保存到 MySQL
[ ] 用户可以查看自己的历史记录
第5周：Agent 工具调用 + 项目亮点
目标：给项目增加一个面试亮点。

[ ] 理解 Agent 工具调用概念
[ ] 设计 study_plan_tool()
[ ] 设计 search_knowledge_base()
[ ] 设计 summarize_document()
[ ] 实现简单工具调用逻辑
[ ] 当用户问学习计划时，调用学习计划工具
[ ] 当用户问资料问题时，调用知识库检索工具
[ ] 优化 Prompt 模板
[ ] 加入错误处理
[ ] 记录项目亮点到 README
验收标准：

[ ] 系统不仅能普通问答，还能进行 RAG 问答
[ ] 系统可以根据问题类型调用简单工具
[ ] 面试时可以讲清楚 Agent 雏形
第6周：简历、GitHub、面试准备
目标：把项目包装到可以投实习的程度。

[ ] 整理 GitHub 仓库
[ ] 编写 README.md
[ ] 添加项目介绍
[ ] 添加技术栈
[ ] 添加功能模块
[ ] 添加启动方式
[ ] 添加接口说明
[ ] 添加项目截图
[ ] 写简历项目描述
[ ] 写 2 分钟项目讲解稿
[ ] 准备 30 个面试问题
[ ] 开始投递实习岗位
验收标准：

[ ] 简历上有完整项目
[ ] GitHub 上有完整代码和 README
[ ] 面试时能讲清楚项目
[ ] 可以开始投递杭州 AI 应用开发相关实习
七、Codex 总任务清单 阶段一：后端基础搭建
[ ] 任务 1：创建 FastAPI 项目结构
[ ] 任务 2：配置 MySQL 数据库连接
[ ] 任务 3：创建数据库表模型
阶段二：用户模块
[ ] 任务 4：实现用户注册接口
[ ] 任务 5：实现用户登录接口
[ ] 任务 6：实现获取当前用户信息接口
阶段三：大模型问答模块
[ ] 任务 7：封装大模型 API 调用
[ ] 任务 8：实现普通 AI 问答接口
[ ] 任务 9：实现聊天历史接口
阶段四：文档上传模块
[ ] 任务 10：实现文档上传接口
[ ] 任务 11：实现文档列表接口
[ ] 任务 12：实现删除文档接口
阶段五：RAG 知识库模块
[ ] 任务 13：实现文档文本提取
[ ] 任务 14：实现文本切分
[ ] 任务 15：实现 Embedding 向量化
[ ] 任务 16：接入 Chroma 向量库
[ ] 任务 17：实现 RAG 问答接口
阶段六：前端项目
[ ] 任务 18：创建 Vue3 前端项目
[ ] 任务 19：实现登录注册页面
[ ] 任务 20：实现聊天页面
[ ] 任务 21：实现知识库页面
阶段七：项目优化
[ ] 任务 22：统一接口返回格式
[ ] 任务 23：添加异常处理
[ ] 任务 24：添加 README 文档
阶段八：面试和简历包装
[ ] 任务 25：生成简历项目描述
[ ] 任务 26：生成项目面试讲解稿
[ ] 任务 27：生成常见面试问题
八、Day 01 已完成记录 Day 01 目标
跑通 FastAPI 后端基础接口。

Day 01 已完成
[x] 创建 backend 后端目录
[x] 创建 Python 虚拟环境
[x] 激活虚拟环境
[x] 安装 fastapi
[x] 安装 uvicorn
[x] 安装 python-dotenv
[x] 安装 requests
[x] 创建 main.py
[x] 实现 GET / 接口
[x] 实现 POST /chat 测试接口
[x] 理解 main.py 基础代码
[x] 理解常用命令含义
Day 01 常用命令 cd H:\pythonPJ\backend .\venv\Scripts\activate uvicorn main:app --reload Day 01 验收标准
[x] 浏览器打开 http://127.0.0.1:8000 能看到启动成功信息
[x] 浏览器打开 http://127.0.0.1:8000/docs 能看到接口文档
[x] POST /chat 输入问题后能返回测试回答
九、Day 02 当前进度 Day 02 目标
将 /chat 接口从固定测试回答改成真实大模型回答。

Day 02 已做
[x] 导入 os
[x] 导入 requests
[x] 导入 load_dotenv
[x] 使用 load_dotenv() 读取 .env 文件
[x] 从 .env 读取 API_KEY
[x] 从 .env 读取 BASE_URL
[x] 从 .env 读取 MODEL_NAME
[x] 封装 ask_llm(question)
[x] 使用 requests.post() 请求大模型接口
[x] 修复返回字段解析错误
Day 02 重要修复
错误写法：

return result["choices"][0]["content"]["content"]
正确写法：

return result["choices"][0]["message"]["content"]
原因：大多数 OpenAI 兼容格式返回结构是：

{ "choices": [ { "message": { "role": "assistant", "content": "AI回答内容" } } ] } Day 02 待完成
[ ] 确认 /chat 能返回真实 AI 回答
[ ] 记录当前可用的 API 配置
[ ] 整理 main.py 代码
[ ] 可选：将 ask_llm 拆分到 services/llm_service.py
十、当前 main.py 核心结构
当前后端主要流程：

FastAPI 接收用户问题 ↓ /chat 接口调用 ask_llm(question) ↓ ask_llm 读取 API_KEY、BASE_URL、MODEL_NAME ↓ requests.post 请求大模型 API ↓ 解析 result["choices"][0]["message"]["content"] ↓ 返回 answer 十一、后续优先级
接下来不要乱加功能，按这个顺序来：

[ ] 先确认大模型 API 调用完全跑通
[ ] 再整理后端目录结构
[ ] 再做 MySQL 聊天记录保存
[ ] 再做 Vue3 简单聊天页面
[ ] 再做文档上传
[ ] 再做 RAG 检索
[ ] 最后做登录注册、Agent、README 和简历包装
十二、每日学习习惯
每天至少完成：

[ ] 一个小功能
[ ] 一次代码运行测试
[ ] 一次 Git 提交
[ ] 一段学习记录
[ ] 一个问题总结
每天结束前记录：

## 今日完成 - [ ] ## 今日遇到的问题 - [ ] ## 解决方法 - [ ] ## 明天计划 - [ ] 十三、最终简历项目描述草稿
项目名称：基于大模型与 RAG 的学习资料智能问答系统

项目描述：

基于 Vue3 + FastAPI + MySQL + Chroma + 大模型 API 实现学习资料智能问答系统。系统支持用户登录、文档上传、文本切分、Embedding 向量化、相似度检索、RAG 问答、聊天记录保存等功能。用户上传学习资料后，系统可根据资料内容进行精准问答，降低大模型幻觉，提高回答的可追溯性。

技术亮点：

[ ] 使用 FastAPI 封装大模型问答接口，实现前后端分离
[ ] 使用文本切分 + Embedding + 向量检索实现 RAG 知识库问答
[ ] 使用 MySQL 保存用户信息、文档信息和聊天记录
[ ] 使用 Vue3 + Element Plus 实现聊天页面和知识库管理页面
[ ] 设计 Prompt 模板，将检索结果拼接进上下文，提高回答准确性
十四、2分钟项目讲解稿草稿
我做的是一个基于大模型和 RAG 的学习资料智能问答系统。这个项目的主要目标是解决普通大模型回答不够贴合个人资料的问题。

用户可以上传自己的学习资料，例如高数、英语、C语言、数据结构相关文档。系统会对文档进行文本提取、切分，然后通过 Embedding 转换成向量并存入向量数据库。

当用户提问时，系统不会直接把问题发给大模型，而是会先根据问题去向量库中检索最相关的资料片段，然后把这些片段和用户问题一起拼接成 Prompt，再交给大模型生成回答。

项目前端使用 Vue3 和 Element Plus，后端使用 Python FastAPI，数据库使用 MySQL，向量库计划使用 Chroma。这个项目的核心流程是文档上传、文本切分、向量化、相似度检索和大模型生成回答。

通过这个项目，我主要练习了 FastAPI 接口开发、大模型 API 调用、Prompt 设计、RAG 检索增强生成、数据库设计和前后端分离开发。

后续我还会继续优化，比如加入用户登录、聊天历史、文档管理、Agent 工具调用和线上部署。

十五、面试重点问题清单 Python / FastAPI
[ ] FastAPI 怎么定义 GET 接口？
[ ] FastAPI 怎么定义 POST 接口？
[ ] BaseModel 的作用是什么？
[ ] requests.post() 是做什么的？
[ ] .env 文件有什么作用？
[ ] python-dotenv 是干什么的？
大模型 API
[ ] API_KEY 是什么？
[ ] BASE_URL 是什么？
[ ] MODEL_NAME 是什么？
[ ] messages 参数是什么？
[ ] system role 和 user role 有什么区别？
[ ] temperature 是什么？
[ ] OpenAI 兼容格式返回结构是什么？
RAG
[ ] 什么是 RAG？
[ ] RAG 为什么可以减少幻觉？
[ ] 什么是 Embedding？
[ ] 什么是向量数据库？
[ ] 什么是文本切分？
[ ] top_k 检索是什么意思？
[ ] RAG 的完整流程是什么？
项目细节
[ ] 你的项目解决什么问题？
[ ] 为什么要做这个项目？
[ ] 你的后端接口有哪些？
[ ] 你的数据库表怎么设计？
[ ] 你的项目怎么调用大模型？
[ ] 你的项目怎么处理长文档？
[ ] 你的项目有什么不足？
[ ] 后续如何优化？
十六、最终验收标准
项目完成后需要满足：

[ ] 后端 FastAPI 可以正常启动
[ ] 前端 Vue3 可以正常启动
[ ] 用户可以注册登录
[ ] 用户可以上传学习资料
[ ] 系统可以提取文档文本
[ ] 系统可以进行文本切分
[ ] 系统可以保存向量
[ ] 用户提问时可以检索相关资料
[ ] 大模型可以基于资料回答问题
[ ] 聊天记录可以保存
[ ] GitHub 有 README
[ ] 简历上可以写这个项目
[ ] 面试时可以讲清楚项目
十七、当前最重要的一句话
现在不要追求一次性做完整项目，先把每一天的小功能跑通。每天完成一个可运行的小功能，6周后就能形成一个可以投实习的 AI 应用项目。