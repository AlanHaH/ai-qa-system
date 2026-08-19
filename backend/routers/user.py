from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from services.auth_service import hash_password, verify_password, create_access_token, require_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 请求体格式
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/user/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        return {"error": "用户名已存在"}

    # 创建新用户（密码加密后存储）
    user = User(
        username=request.username,
        password=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "注册成功", "user_id": user.id}


@router.post("/user/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "用户名或密码错误"}

    # 验证密码
    if not verify_password(request.password, user.password):
        return {"error": "用户名或密码错误"}

    # 生成 JWT token（sub 必须是字符串）
    token = create_access_token({"sub": str(user.id)})

    return {
        "message": "登录成功",
        "token": token,
        "user_id": user.id,
        "username": user.username
    }


@router.get("/user/me")
def get_current_user(user_id: int = Depends(require_user), db: Session = Depends(get_db)):
    """获取当前用户信息（强制登录验证）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "用户不存在"}

    return {
        "user_id": user.id,
        "username": user.username,
        "created_at": str(user.created_at)
    }
