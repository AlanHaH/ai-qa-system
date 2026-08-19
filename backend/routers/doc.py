from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document
from services.doc_service import extract_text
from services.rag_service import add_document, delete_document
from services.auth_service import require_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/doc/upload")
async def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """上传文档，提取文本并保存到数据库"""
    content = await file.read()

    # 限制文件大小为 10MB
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        return {"error": "文件太大，最大支持 10MB"}

    text = extract_text(content, file.filename)

    doc = Document(user_id=user_id, filename=file.filename, content=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 同步存入向量库（切分 + 向量化，带用户和文档来源）
    add_document(doc.id, text, user_id, file.filename)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "message": "上传成功"
    }


@router.get("/doc/list")
def doc_list(db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """查询当前用户的文档列表"""
    docs = db.query(Document).filter(
        Document.user_id == user_id
    ).order_by(Document.id.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "created_at": str(d.created_at)
        }
        for d in docs
    ]


@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db), user_id: int = Depends(require_user)):
    """删除指定文档"""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()
    if not doc:
        return {"error": "文档不存在"}

    # 同步删除向量库中的数据（按用户隔离）
    delete_document(doc_id, user_id)

    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}
