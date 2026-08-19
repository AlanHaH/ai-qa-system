import threading

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

COLLECTION_NAME = "documents"

# Chroma 写入锁：多个文档后台异步向量化时串行写，避免并发写冲突
_write_lock = threading.Lock()

# 初始化 Chroma 向量库（数据存在 backend/chroma_db 目录）
# ChromaDB 自带 Embedding 功能，不需要调外部 API
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# LangChain 封装现有 collection（不传 embedding_function，默认即 all-MiniLM-L6-v2，
# 与旧数据写入时 ChromaDB 默认 embedding 完全一致，旧向量检索不受影响）
vectorstore = Chroma(client=chroma_client, collection_name=COLLECTION_NAME)


def _get_splitter() -> RecursiveCharacterTextSplitter:
    """中文友好的递归切分器（500 字符 / 50 重叠）"""
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )


def add_document(doc_id: int, text: str, user_id: int = 0, filename: str = ""):
    """
    把文档切分后存入向量库，并记录用户和文档来源。
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
        vectorstore.add_documents(docs, ids=ids)


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
