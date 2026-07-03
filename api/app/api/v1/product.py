"""
商品模块API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductQuery
from app.schemas.response import success_response, error_response
from app.service.product_service import ProductService
from app.service.user_service import BusinessException
from app.utils.jwt import get_current_user_id, get_current_user_id_optional
from app.config.constants import ErrorCode

router = APIRouter()


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取商品分类树"""
    try:
        result = ProductService.get_category_tree(db)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/list")
async def get_product_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None, description="关键词"),
    min_price: Optional[float] = Query(None, ge=0, description="最低价格"),
    max_price: Optional[float] = Query(None, ge=0, description="最高价格"),
    condition: Optional[int] = Query(None, ge=1, le=5, description="成色"),
    sort_by: Optional[str] = Query("create_time", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方式"),
    seller_id: Optional[int] = Query(None, description="卖家ID"),
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    try:
        query_params = ProductQuery(
            page=page,
            page_size=page_size,
            category_id=category_id,
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            condition=condition,
            sort_by=sort_by,
            sort_order=sort_order,
            seller_id=seller_id
        )
        result = ProductService.get_product_list(db, query_params, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/{product_id}")
async def get_product_detail(
    product_id: int,
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """获取商品详情"""
    try:
        result = ProductService.get_product_detail(db, product_id, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("")
async def create_product(
    product_data: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """发布商品"""
    try:
        result = ProductService.create_product(db, user_id, product_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    update_data: ProductUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新商品"""
    try:
        result = ProductService.update_product(db, product_id, user_id, update_data)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除/下架商品"""
    try:
        result = ProductService.delete_product(db, product_id, user_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/{product_id}/favorite")
async def toggle_favorite(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """收藏/取消收藏商品"""
    try:
        result = ProductService.toggle_favorite(db, user_id, product_id)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/my/favorites")
async def get_my_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取我的收藏列表"""
    try:
        result = ProductService.get_my_favorites(db, user_id, page, page_size)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/my/products")
async def get_my_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="商品状态"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取我发布的商品"""
    try:
        result = ProductService.get_my_products(db, user_id, page, page_size, status)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/hot/list")
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db)
):
    """获取热门商品"""
    try:
        result = ProductService.get_hot_products(db, limit)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/new/list")
async def get_new_products(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db)
):
    """获取最新商品"""
    try:
        result = ProductService.get_new_products(db, limit)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
