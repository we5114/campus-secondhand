"""
大模型模块API路由
"""
from fastapi import APIRouter, Depends, Body
from typing import Optional, List

from app.schemas.response import success_response, error_response
from app.service.llm_service import LLMService
from app.service.user_service import BusinessException
from app.utils.jwt import get_current_user_id
from app.config.constants import ErrorCode

router = APIRouter()


@router.post("/chat")
async def chat_with_ai(
    message: str = Body(..., description="用户消息"),
    history: Optional[list] = Body(None, description="对话历史"),
    system_prompt: Optional[str] = Body(None, description="系统提示词"),
    user_id: int = Depends(get_current_user_id)
):
    """与AI对话（智能客服）"""
    try:
        result = await LLMService.chat_with_ai(message, history, system_prompt)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/generate-description")
async def generate_product_description(
    title: str = Body(..., description="商品标题"),
    category: str = Body(..., description="商品分类"),
    condition: str = Body(..., description="商品成色"),
    price: float = Body(..., description="售价"),
    original_price: Optional[float] = Body(None, description="原价"),
    features: Optional[List[str]] = Body(None, description="商品特点列表"),
    user_id: int = Depends(get_current_user_id)
):
    """生成商品描述"""
    try:
        result = await LLMService.generate_product_description(
            title, category, condition, price, original_price, features
        )
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/moderation")
async def content_moderation(
    content: str = Body(..., description="待审核内容"),
    user_id: int = Depends(get_current_user_id)
):
    """内容审核"""
    try:
        result = await LLMService.content_moderation(content)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/smart-pricing")
async def smart_pricing(
    category: str = Body(..., description="商品分类"),
    condition: str = Body(..., description="成色"),
    original_price: float = Body(..., description="原价"),
    age_months: int = Body(0, description="使用时长（月）"),
    brand: Optional[str] = Body(None, description="品牌"),
    user_id: int = Depends(get_current_user_id)
):
    """智能定价建议"""
    try:
        result = await LLMService.smart_pricing(category, condition, original_price, age_months, brand)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))


@router.post("/sentiment")
async def sentiment_analysis(
    text: str = Body(..., description="待分析文本"),
    user_id: int = Depends(get_current_user_id)
):
    """情感分析"""
    try:
        result = await LLMService.sentiment_analysis(text)
        return success_response(result)
    except BusinessException as e:
        return error_response(e.code, e.message)
    except Exception as e:
        return error_response(ErrorCode.SYSTEM_ERROR, str(e))
