"""
管理后台API路由
"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.models import get_db
from app.schemas.response import success_response, error_response
from app.service.admin_service import AdminService
from app.service.user_service import BusinessException
from app.config.constants import ErrorCode

router = APIRouter()


# ==================== 仪表盘 ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """获取仪表盘统计数据"""
    try:
        result = AdminService.get_dashboard_stats(db)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/dashboard/sales-trend")
async def get_sales_trend(
    days: int = Query(7, ge=1, le=30, description="天数"),
    db: Session = Depends(get_db)
):
    """获取销售趋势数据"""
    try:
        result = AdminService.get_sales_trend(db, days)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/dashboard/category-stats")
async def get_category_stats(
    db: Session = Depends(get_db)
):
    """获取分类统计数据"""
    try:
        result = AdminService.get_category_stats(db)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 用户管理 ====================

@router.get("/users")
async def get_user_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[int] = Query(None, description="用户状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    try:
        result = AdminService.get_user_list(db, keyword, status, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status: int = Body(..., description="状态"),
    db: Session = Depends(get_db)
):
    """更新用户状态"""
    try:
        result = AdminService.update_user_status(db, user_id, status)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 实名认证管理 ====================

@router.get("/real-name")
async def get_real_name_list(
    status: Optional[int] = Query(None, description="审核状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取实名认证列表"""
    try:
        result = AdminService.get_real_name_list(db, status, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/real-name/{id}/audit")
async def audit_real_name(
    id: int,
    status: int = Body(..., description="审核状态：1-通过 2-拒绝"),
    remark: Optional[str] = Body(None, description="审核备注"),
    db: Session = Depends(get_db)
):
    """审核实名认证"""
    try:
        result = AdminService.audit_real_name(db, id, status, remark)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 商品管理 ====================

@router.get("/products")
async def get_product_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[int] = Query(None, description="商品状态"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    try:
        result = AdminService.get_product_list(db, keyword, status, category_id, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/products/{product_id}/status")
async def update_product_status(
    product_id: int,
    status: int = Body(..., description="状态"),
    db: Session = Depends(get_db)
):
    """更新商品状态"""
    try:
        result = AdminService.update_product_status(db, product_id, status)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/products/{product_id}/recommend")
async def set_product_recommend(
    product_id: int,
    is_recommend: int = Body(..., description="是否推荐：0-否 1-是"),
    db: Session = Depends(get_db)
):
    """设置商品推荐"""
    try:
        result = AdminService.set_product_recommend(db, product_id, is_recommend)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 订单管理 ====================

@router.get("/orders")
async def get_order_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[int] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    try:
        result = AdminService.get_order_list(db, keyword, status, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
