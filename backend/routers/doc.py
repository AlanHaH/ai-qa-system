from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
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
async def upload_doc(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_user),
):
    """上传文档：落库后立即返回，文本提取 + 向量化交给后台任务执行"""
    content = await file.read()

    # 限制文件大小为 30MB（与 nginx client_max_body_size、前端提示一致）
    max_size = 30 * 1024 * 1024  # 30MB
    if len(content) > max_size:
        return {"error": "文件太大，最大支持 30MB"}

    # 先落库（status=processing，content 稍后由后台任务填充）
    doc = Document(user_id=user_id, filename=file.filename, content="", status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 后台执行：文本提取 + 切分向量化 + 更新状态（FastAPI 自动用线程池跑同步函数）
    background_tasks.add_task(process_document, doc.id, content, file.filename, user_id)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": "processing",
        "message": "上传成功，正在后台向量化"
    }


def process_document(doc_id: int, raw_bytes: bytes, filename: str, user_id: int):
    """
    后台任务：提取文本 → 存入向量库 → 更新状态。
    自行开数据库会话（请求的 get_db 会话在响应返回后已关闭）。
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(
            Document.id == doc_id, Document.user_id == user_id
        ).first()
        if not doc:
            return  # 文档已被删除，跳过

        text = extract_text(raw_bytes, filename)
        doc.content = text
        db.commit()

        add_document(doc_id, text, user_id, filename)
        doc.status = "completed"
        db.commit()
    except Exception as e:
        db.rollback()
        # 记录失败状态
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "failed"
            db.commit()
    finally:
        db.close()


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
            "status": d.status,
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
