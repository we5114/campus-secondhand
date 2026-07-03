"""
订单模块API路由
"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models import get_db
from app.schemas.response import success_response, error_response
from app.service.order_service import OrderService
from app.service.user_service import BusinessException
from app.utils.jwt import get_current_user_id
from app.config.constants import ErrorCode

router = APIRouter()


@router.post("")
async def create_order(
    product_id: int = Body(..., description="商品ID"),
    quantity: int = Body(1, ge=1, description="数量"),
    remark: Optional[str] = Body(None, description="备注"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建订单"""
    try:
        result = OrderService.create_order(db, user_id, product_id, quantity, remark)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/list")
async def get_order_list(
    status: Optional[int] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: str = Query("buyer", description="角色：buyer-买家 seller-卖家"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    try:
        result = OrderService.get_order_list(db, user_id, status, page, page_size, role)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/{order_id}")
async def get_order_detail(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    try:
        result = OrderService.get_order_detail(db, order_id, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    pay_type: int = Body(3, description="支付方式：1-微信 2-支付宝 3-线下支付"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """支付订单"""
    try:
        result = OrderService.pay_order(db, order_id, user_id, pay_type)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    reason: Optional[str] = Body(None, description="取消原因"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """取消订单"""
    try:
        result = OrderService.cancel_order(db, order_id, user_id, reason)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{order_id}/ship")
async def ship_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """发货（卖家）"""
    try:
        result = OrderService.ship_order(db, order_id, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{order_id}/confirm")
async def confirm_receipt(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """确认收货"""
    try:
        result = OrderService.confirm_receipt(db, order_id, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{order_id}/refund")
async def apply_refund(
    order_id: int,
    reason: str = Body(..., description="退款原因"),
    description: Optional[str] = Body(None, description="退款说明"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """申请退款"""
    try:
        result = OrderService.apply_refund(db, order_id, user_id, reason, description)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 购物车相关 ====================

@router.get("/cart/list")
async def get_cart_list(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取购物车列表"""
    try:
        result = OrderService.get_cart_list(db, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/cart/add")
async def add_to_cart(
    product_id: int = Body(..., description="商品ID"),
    quantity: int = Body(1, ge=1, description="数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """添加到购物车"""
    try:
        result = OrderService.add_to_cart(db, user_id, product_id, quantity)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/cart/{cart_id}")
async def update_cart_item(
    cart_id: int,
    quantity: int = Body(..., ge=0, description="数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新购物车数量"""
    try:
        result = OrderService.update_cart_item(db, user_id, cart_id, quantity)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.delete("/cart")
async def remove_from_cart(
    cart_ids: List[int] = Body(..., description="购物车项ID列表"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """从购物车移除"""
    try:
        result = OrderService.remove_from_cart(db, user_id, cart_ids)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


# ==================== 评价相关 ====================

@router.post("/{order_id}/review")
async def create_review(
    order_id: int,
    rating: int = Body(..., ge=1, le=5, description="评分"),
    content: Optional[str] = Body(None, description="评价内容"),
    images: Optional[List[str]] = Body(None, description="评价图片"),
    is_anonymous: int = Body(0, description="是否匿名"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建评价"""
    try:
        result = OrderService.create_review(db, order_id, user_id, rating, content, images, is_anonymous)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/product/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取商品评价列表"""
    try:
        result = OrderService.get_product_reviews(db, product_id, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
