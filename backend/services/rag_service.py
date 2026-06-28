import chromadb

# 初始化 Chroma 向量库（数据存在 backend/chroma_db 目录）
# ChromaDB 自带 Embedding 功能，不需要调外部 API
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")


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


def add_document(doc_id: int, text: str):
    """
    把文档切分后存入向量库。
    ChromaDB 会自动把文本转换成向量，不需要手动调 Embedding API。
    """
    chunks = split_text(text)
    for i, chunk in enumerate(chunks):
        # ChromaDB 自动处理 Embedding
        collection.add(
            ids=[f"doc_{doc_id}_chunk_{i}"],
            documents=[chunk]
        )


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


def search_similar(question: str, top_k: int = 3) -> list:
    """
    根据用户问题，从向量库检索最相关的文档片段。
    top_k — 返回最相似的前 k 个结果
    """
    # ChromaDB 自动把问题转换成向量，然后检索
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    return results["documents"][0] if results["documents"] else []
