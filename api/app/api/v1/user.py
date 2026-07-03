"""
用户模块API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time

from app.models import get_db
from app.schemas.user_schema import UserRegister, UserLogin, UserUpdate, PasswordUpdate, RealNameApply
from app.schemas.response import success_response, error_response
from app.service.user_service import UserService, BusinessException
from app.utils.jwt import get_current_user_id
from app.config.constants import ErrorCode

router = APIRouter()


@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        result = UserService.register(db, user_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        result = UserService.login(db, login_data.username, login_data.password)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/admin/login")
async def admin_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """管理员登录"""
    try:
        result = UserService.admin_login(db, login_data.username, login_data.password)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/info")
async def get_user_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    try:
        result = UserService.get_user_info(db, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/info")
async def update_user_info(
    update_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    try:
        result = UserService.update_user_info(db, user_id, update_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """修改密码"""
    try:
        result = UserService.update_password(db, user_id, password_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/{user_id}")
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户详情（公开信息）"""
    try:
        result = UserService.get_user_detail(db, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/real-name")
async def apply_real_name(
    real_name_data: RealNameApply,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """申请实名认证"""
    try:
        result = UserService.apply_real_name(db, user_id, real_name_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
