import os
import threading

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

COLLECTION_NAME = "documents"

# Chroma 写入锁：多个文档后台异步向量化时串行写，避免并发写冲突
_write_lock = threading.Lock()

# 初始化 Chroma 向量库（数据存在 backend/chroma_db 目录）
chroma_client = chromadb.PersistentClient(path="chroma_db")

# 云端 embedding（硅基流动 SiliconFlow，OpenAI 兼容）：
# 配置 EMBEDDING_API_KEY 后，embedding 计算走云端 API，服务器不加载本地模型，
# 内存/CPU 压力大幅下降（适合低配服务器，大文件向量化不再卡）。
# 未配置 key 时回退 ChromaDB 内置本地模型（all-MiniLM-L6-v2）。
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

if EMBEDDING_API_KEY:
    from langchain_openai import OpenAIEmbeddings
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=EMBEDDING_API_KEY,
        base_url=EMBEDDING_BASE_URL,
    )
else:
    embedding_function = None

collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
vectorstore = Chroma(
    client=chroma_client,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


def _get_splitter() -> RecursiveCharacterTextSplitter:
    """中文友好的递归切分器（500 字符 / 50 重叠）"""
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )


def add_document(doc_id: int, text: str, user_id: int = 0, filename: str = "", batch_size: int = 300):
    """
    把文档切分后分批存入向量库，并记录用户和文档来源。
    分批写入（每次 batch_size 片）可显著降低大文件向量化的内存峰值，避免低内存服务器卡死。
    """
    chunks = _get_splitter().split_text(text)
    if not chunks:
        return
    docs = [
        Document(
            page_content=c,
            metadata={"user_id": user_id, "doc_id": doc_id, "filename": filename},
        )
        for c in chunks
    ]
    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
    with _write_lock:
        for i in range(0, len(docs), batch_size):
            vectorstore.add_documents(docs[i:i + batch_size], ids=ids[i:i + batch_size])


def delete_document(doc_id: int, user_id: int = 0):
    """
    从向量库删除指定文档的所有片段（按用户隔离）。
    用原生 collection 按 doc_id + user_id 过滤取 ids，再走 LangChain 删除。
    """
    # ChromaDB where 多条件必须用 $and
    data = collection.get(where={"$and": [{"doc_id": doc_id}, {"user_id": user_id}]})
    ids_to_delete = data.get("ids") or []
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)


def search_similar(question: str, top_k: int = 3, user_id: int = None) -> list:
    """
    根据用户问题，从向量库检索最相关的文档片段（只查当前用户的知识库）。
    返回带来源信息的片段列表：[{content, filename}]
    """
    filter_ = {"user_id": user_id} if user_id is not None else None
    results = vectorstore.similarity_search(question, k=top_k, filter=filter_)
    return [
        {
            "content": doc.page_content,
            "filename": doc.metadata.get("filename", ""),
        }
        for doc in results
    ]
