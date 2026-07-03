"""
聊天模块API路由
"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.models import get_db
from app.schemas.response import success_response, error_response
from app.service.chat_service import ChatService
from app.service.user_service import BusinessException
from app.utils.jwt import get_current_user_id
from app.config.constants import ErrorCode

router = APIRouter()


@router.get("/sessions")
async def get_session_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取聊天会话列表"""
    try:
        result = ChatService.get_session_list(db, user_id, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/messages/{other_user_id}")
async def get_message_list(
    other_user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取聊天消息列表"""
    try:
        result = ChatService.get_message_list(db, user_id, other_user_id, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/send")
async def send_message(
    to_user_id: int = Body(..., description="接收者ID"),
    content: str = Body(..., description="消息内容"),
    msg_type: int = Body(1, description="消息类型：1-文本 2-图片 3-语音"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """发送消息"""
    try:
        result = ChatService.send_message(db, user_id, to_user_id, content, msg_type)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/read/{other_user_id}")
async def mark_as_read(
    other_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    try:
        result = ChatService.mark_as_read(db, user_id, other_user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/unread")
async def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取未读消息数"""
    try:
        result = ChatService.get_unread_count(db, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/system")
async def get_system_messages(
    msg_type: Optional[int] = Query(None, description="消息类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取系统消息列表"""
    try:
        result = ChatService.get_system_messages(db, user_id, msg_type, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
