"""
通用响应模型
"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    timestamp: int = 0

    class Config:
        schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {},
                "timestamp": 1719000000
            }
        }


class PageData(BaseModel, Generic[T]):
    """分页数据模型"""
    list: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp())
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp())
    }
