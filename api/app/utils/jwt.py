"""
JWT工具类
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.config.constants import ErrorCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login", auto_error=False)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = {"user_id": user_id, "type": "access"}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """创建刷新令牌"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"user_id": user_id, "type": "refresh", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """获取当前用户ID"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.USER_NOT_LOGIN, "message": "用户未登录"}
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.USER_TOKEN_INVALID, "message": "Token无效"}
        )

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.USER_TOKEN_INVALID, "message": "Token无效"}
        )

    # 检查是否过期
    exp = payload.get("exp")
    if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ErrorCode.USER_TOKEN_EXPIRED, "message": "Token已过期"}
        )

    return user_id


def get_current_user_id_optional(token: str = Depends(oauth2_scheme)) -> Optional[int]:
    """获取当前用户ID（可选，未登录返回None）"""
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if user_id is None:
        return None

    # 检查是否过期
    exp = payload.get("exp")
    if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
        return None

    return user_id
