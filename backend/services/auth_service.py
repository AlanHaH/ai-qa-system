import os
from datetime import datetime, timedelta
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
