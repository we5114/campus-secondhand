"""
商品相关Pydantic模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求模型 ====================

class ProductCreate(BaseModel):
    """商品发布请求"""
    category_id: int = Field(..., description="分类ID")
    title: str = Field(..., min_length=1, max_length=100, description="商品标题")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., gt=0, description="售价")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    condition: int = Field(..., ge=1, le=5, description="成色：1-全新 2-九成新 3-八成新 4-七成新 5-其他")
    quality: Optional[str] = Field(None, max_length=255, description="质量描述")
    trade_type: Optional[int] = Field(1, ge=1, le=3, description="交易方式：1-面交 2-邮寄 3-均可")
    location: Optional[str] = Field(None, max_length=100, description="交易地点")
    images: List[str] = Field(default=[], description="商品图片列表")


class ProductUpdate(BaseModel):
    """商品更新请求"""
    category_id: Optional[int] = Field(None, description="分类ID")
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="商品标题")
    description: Optional[str] = Field(None, description="商品描述")
    price: Optional[float] = Field(None, gt=0, description="售价")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    condition: Optional[int] = Field(None, ge=1, le=5, description="成色")
    quality: Optional[str] = Field(None, max_length=255, description="质量描述")
    trade_type: Optional[int] = Field(None, ge=1, le=3, description="交易方式")
    location: Optional[str] = Field(None, max_length=100, description="交易地点")
    images: Optional[List[str]] = Field(None, description="商品图片列表")
    status: Optional[int] = Field(None, ge=0, le=2, description="状态：0-上架 2-下架")


class ProductQuery(BaseModel):
    """商品查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    category_id: Optional[int] = Field(None, description="分类ID")
    keyword: Optional[str] = Field(None, description="关键词")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    condition: Optional[int] = Field(None, ge=1, le=5, description="成色")
    sort_by: Optional[str] = Field("create_time", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方式：asc/desc")
    seller_id: Optional[int] = Field(None, description="卖家ID")


# ==================== 响应模型 ====================

class CategoryInfo(BaseModel):
    """分类信息"""
    id: int
    name: str
    parent_id: int
    level: int
    icon: Optional[str] = None
    sort: int = 0

    class Config:
        orm_mode = True


class ProductImageInfo(BaseModel):
    """商品图片信息"""
    id: int
    image_url: str
    sort: int = 0
    is_cover: int = 0

    class Config:
        orm_mode = True


class ProductInfo(BaseModel):
    """商品列表信息"""
    id: int
    seller_id: int
    category_id: int
    title: str
    price: float
    original_price: Optional[float] = None
    condition: int
    status: int
    view_count: int = 0
    favorite_count: int = 0
    chat_count: int = 0
    is_top: int = 0
    is_recommend: int = 0
    create_time: Optional[datetime] = None
    cover_image: Optional[str] = None
    seller_name: Optional[str] = None
    category_name: Optional[str] = None

    class Config:
        orm_mode = True


class ProductDetail(BaseModel):
    """商品详情"""
    id: int
    seller_id: int
    category_id: int
    title: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    condition: int
    quality: Optional[str] = None
    trade_type: int = 1
    location: Optional[str] = None
    status: int
    view_count: int = 0
    favorite_count: int = 0
    chat_count: int = 0
    is_top: int = 0
    is_recommend: int = 0
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    images: List[ProductImageInfo] = []
    seller: Optional[dict] = None
    category: Optional[CategoryInfo] = None
    is_favorite: bool = False

    class Config:
        orm_mode = True
