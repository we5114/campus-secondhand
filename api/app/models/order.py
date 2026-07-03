"""
订单相关数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Text, DECIMAL
from sqlalchemy.sql import func

from app.models import BaseModel


class Cart(BaseModel):
    """购物车表"""
    __tablename__ = "cart"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="购物车ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    quantity = Column(Integer, default=1, comment="数量")
    selected = Column(SmallInteger, default=1, comment="是否选中：0-否 1-是")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class OrderInfo(BaseModel):
    """订单表"""
    __tablename__ = "order_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(64), nullable=False, unique=True, comment="订单编号")
    buyer_id = Column(BigInteger, nullable=False, comment="买家ID")
    seller_id = Column(BigInteger, nullable=False, comment="卖家ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    product_title = Column(String(100), nullable=True, comment="商品标题快照")
    product_image = Column(String(255), nullable=True, comment="商品图片快照")
    product_price = Column(DECIMAL(10, 2), nullable=True, comment="商品单价快照")
    quantity = Column(Integer, default=1, comment="购买数量")
    total_amount = Column(DECIMAL(10, 2), nullable=False, comment="订单总金额")
    pay_amount = Column(DECIMAL(10, 2), nullable=True, comment="实付金额")
    freight_amount = Column(DECIMAL(10, 2), default=0, comment="运费")
    discount_amount = Column(DECIMAL(10, 2), default=0, comment="优惠金额")
    pay_type = Column(SmallInteger, default=0, comment="支付方式：0-未支付 1-微信 2-支付宝 3-线下支付")
    trade_type = Column(SmallInteger, default=1, comment="交易方式：1-面交 2-邮寄")
    status = Column(SmallInteger, default=0, comment="订单状态：0-待付款 1-待发货 2-待收货 3-已完成 4-已取消 5-退款中 6-已退款")
    receiver_name = Column(String(50), nullable=True, comment="收货人姓名")
    receiver_phone = Column(String(20), nullable=True, comment="收货人电话")
    receiver_address = Column(String(255), nullable=True, comment="收货地址")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    ship_time = Column(DateTime, nullable=True, comment="发货时间")
    finish_time = Column(DateTime, nullable=True, comment="完成时间")
    cancel_time = Column(DateTime, nullable=True, comment="取消时间")
    cancel_reason = Column(String(255), nullable=True, comment="取消原因")
    remark = Column(String(255), nullable=True, comment="订单备注")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class OrderLog(BaseModel):
    """订单日志表"""
    __tablename__ = "order_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    order_id = Column(BigInteger, nullable=False, comment="订单ID")
    operator_id = Column(BigInteger, nullable=True, comment="操作人ID")
    operator_type = Column(SmallInteger, default=0, comment="操作人类型：0-系统 1-买家 2-卖家 3-管理员")
    action = Column(String(50), nullable=False, comment="操作动作")
    content = Column(String(500), nullable=True, comment="操作内容")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")


class Refund(BaseModel):
    """退款表"""
    __tablename__ = "refund"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="退款ID")
    refund_no = Column(String(64), nullable=False, unique=True, comment="退款编号")
    order_id = Column(BigInteger, nullable=False, comment="订单ID")
    user_id = Column(BigInteger, nullable=False, comment="申请人ID")
    refund_amount = Column(DECIMAL(10, 2), nullable=False, comment="退款金额")
    refund_reason = Column(String(255), nullable=True, comment="退款原因")
    refund_desc = Column(Text, nullable=True, comment="退款说明")
    status = Column(SmallInteger, default=0, comment="状态：0-待处理 1-同意 2-拒绝 3-退款中 4-已完成")
    audit_user_id = Column(BigInteger, nullable=True, comment="审核人ID")
    audit_time = Column(DateTime, nullable=True, comment="审核时间")
    audit_remark = Column(String(255), nullable=True, comment="审核备注")
    refund_time = Column(DateTime, nullable=True, comment="退款完成时间")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Review(BaseModel):
    """评价表"""
    __tablename__ = "review"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="评价ID")
    order_id = Column(BigInteger, nullable=False, comment="订单ID")
    product_id = Column(BigInteger, nullable=False, comment="商品ID")
    user_id = Column(BigInteger, nullable=False, comment="评价人ID")
    to_user_id = Column(BigInteger, nullable=False, comment="被评价人ID")
    rating = Column(SmallInteger, nullable=False, comment="评分：1-5星")
    content = Column(Text, nullable=True, comment="评价内容")
    images = Column(Text, nullable=True, comment="评价图片（JSON格式）")
    type = Column(SmallInteger, default=1, comment="评价类型：1-买家评价卖家 2-卖家评价买家")
    is_anonymous = Column(SmallInteger, default=0, comment="是否匿名：0-否 1-是")
    status = Column(SmallInteger, default=0, comment="状态：0-正常 1-删除")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
