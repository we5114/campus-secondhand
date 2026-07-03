"""
商品相关数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Text, DECIMAL
from sqlalchemy.sql import func

from app.models import BaseModel


class ProductCategory(BaseModel):
    """商品分类表"""
    __tablename__ = "product_category"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    parent_id = Column(Integer, default=0, comment="父分类ID，0表示一级分类")
    level = Column(SmallInteger, default=1, comment="分类层级：1-一级 2-二级 3-三级")
    icon = Column(String(255), nullable=True, comment="分类图标")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(SmallInteger, default=0, comment="状态：0-正常 1-禁用")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Product(BaseModel):
    """商品表"""
    __tablename__ = "product"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="商品ID")
    seller_id = Column(BigInteger, nullable=False, comment="卖家ID")
    category_id = Column(Integer, nullable=False, comment="分类ID")
    title = Column(String(100), nullable=False, comment="商品标题")
    description = Column(Text, nullable=True, comment="商品描述")
    price = Column(DECIMAL(10, 2), nullable=False, comment="售价")
    original_price = Column(DECIMAL(10, 2), nullable=True, comment="原价")
    condition = Column(SmallInteger, nullable=False, comment="成色：1-全新 2-九成新 3-八成新 4-七成新 5-其他")
    quality = Column(String(255), nullable=True, comment="质量描述")
    trade_type = Column(SmallInteger, default=1, comment="交易方式：1-面交 2-邮寄 3-均可")
    location = Column(String(100), nullable=True, comment="交易地点")
    status = Column(SmallInteger, default=0, comment="状态：0-上架 1-已售 2-下架 3-审核中 4-违规")
    view_count = Column(Integer, default=0, comment="浏览量")
    favorite_count = Column(Integer, default=0, comment="收藏数")
    chat_count = Column(Integer, default=0, comment="咨询数")
    is_top = Column(SmallInteger, default=0, comment="是否置顶：0-否 1-是")
    is_recommend = Column(SmallInteger, default=0, comment="是否推荐：0-否 1-是")
    audit_status = Column(SmallInteger, default=0, comment="审核状态：0-待审核 1-通过 2-拒绝")
    audit_user_id = Column(BigInteger, nullable=True, comment="审核人ID")
    audit_time = Column(DateTime, nullable=True, comment="审核时间")
    audit_remark = Column(String(255), nullable=True, comment="审核备注")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ProductImage(BaseModel):
    """商品图片表"""
    __tablename__ = "product_image"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="图片ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    image_url = Column(String(255), nullable=False, comment="图片URL")
    sort = Column(Integer, default=0, comment="排序")
    is_cover = Column(SmallInteger, default=0, comment="是否封面：0-否 1-是")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")


class ProductCollection(BaseModel):
    """商品收藏表"""
    __tablename__ = "product_collection"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")


class ProductTag(BaseModel):
    """商品标签表"""
    __tablename__ = "product_tag"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="标签ID")
    name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    type = Column(SmallInteger, default=1, comment="标签类型：1-系统标签 2-自定义标签")
    use_count = Column(Integer, default=0, comment="使用次数")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")


class ProductTagRelation(BaseModel):
    """商品标签关联表"""
    __tablename__ = "product_tag_relation"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    tag_id = Column(Integer, nullable=False, comment="标签ID")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
