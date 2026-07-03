"""
推荐模块API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models import get_db
from app.schemas.response import success_response, error_response
from app.service.recommend_service import RecommendService
from app.service.user_service import BusinessException
from app.utils.jwt import get_current_user_id, get_current_user_id_optional
from app.config.constants import ErrorCode

router = APIRouter()


@router.get("/home")
async def get_home_recommend(
    limit: int = Query(20, ge=1, le=50, description="推荐数量"),
    user_id: Optional[int] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """获取首页推荐商品"""
    try:
        result = RecommendService.get_home_recommend(db, user_id, limit)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: int,
    limit: int = Query(10, ge=1, le=30, description="推荐数量"),
    db: Session = Depends(get_db)
):
    """获取相似商品推荐"""
    try:
        result = RecommendService.get_similar_products(db, product_id, limit)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.get("/personalized")
async def get_personalized_recommend(
    limit: int = Query(20, ge=1, le=50, description="推荐数量"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取个性化推荐（需要登录）"""
    try:
        result = RecommendService.get_personalized_recommend(db, user_id, limit)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
