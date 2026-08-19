import os
from datetime import datetime, timedelta
from fastapi import Header, HTTPException
from jose import JWTError, jwt
import bcrypt

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境要换成复杂的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # token 有效期 24 小时


def hash_password(password: str) -> str:
    """把明文密码加密成 bcrypt 哈希"""
    # bcrypt 需要 bytes 类型，所以 encode()
    # gensalt() 生成随机盐
    # hashpw() 加密
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码：明文密码 vs 加密后的密码"""
    # checkpw() 验证明文和哈希是否匹配
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """生成 JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解析 JWT token，返回 payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str) -> int:
    """从 token 中获取当前用户 ID"""
    payload = decode_access_token(token)
    if not payload:
        return None
    # sub 是字符串，转成整数
    try:
        return int(payload.get("sub"))
    except (ValueError, TypeError):
        return None


def require_user(authorization: str = Header(None)) -> int:
    """强制登录验证依赖：无 token 或 token 无效/过期时抛 401"""
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="token 无效或已过期")
    return user_id
