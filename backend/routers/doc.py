from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document
from services.doc_service import extract_text
from services.rag_service import add_document

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/doc/upload")
async def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传文档，提取文本并保存到数据库"""
    content = await file.read()

    # 限制文件大小为 10MB
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        return {"error": "文件太大，最大支持 10MB"}

    text = extract_text(content, file.filename)

    doc = Document(filename=file.filename, content=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 同步存入向量库（切分 + 向量化）
    add_document(doc.id, text)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "message": "上传成功"
    }


@router.get("/doc/list")
def doc_list(db: Session = Depends(get_db)):
    """查询所有文档列表"""
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "created_at": str(d.created_at)
        }
        for d in docs
    ]


@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    """删除指定文档"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "文档不存在"}
    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}
