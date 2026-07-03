"""
订单服务层
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func

from app.models.order import OrderInfo, OrderLog, Refund, Cart, Review
from app.models.product import Product, ProductImage
from app.models.user import User
from app.config.constants import ErrorCode, OrderStatus, PayType, RefundStatus
from app.utils.common import generate_order_no, generate_refund_no, calculate_page
from app.service.user_service import BusinessException


class OrderService:
    """订单服务类"""

    @staticmethod
    def create_order(db: Session, buyer_id: int, product_id: int, quantity: int = 1, remark: str = None) -> dict:
        """
        创建订单

        Args:
            db: 数据库会话
            buyer_id: 买家ID
            product_id: 商品ID
            quantity: 数量
            remark: 备注

        Returns:
            订单信息
        """
        # 检查商品是否存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        # 检查商品状态
        if product.status != 0:  # 0-上架
            raise BusinessException(ErrorCode.PRODUCT_OFF_SHELF, "商品已下架")

        # 检查是否是自己的商品
        if product.seller_id == buyer_id:
            raise BusinessException(ErrorCode.PARAM_ERROR, "不能购买自己的商品")

        # 计算金额
        total_amount = product.price * quantity
        pay_amount = total_amount

        # 创建订单
        order_no = generate_order_no()
        new_order = OrderInfo(
            order_no=order_no,
            buyer_id=buyer_id,
            seller_id=product.seller_id,
            product_id=product_id,
            product_title=product.title,
            product_price=product.price,
            quantity=quantity,
            total_amount=total_amount,
            pay_amount=pay_amount,
            status=OrderStatus.PENDING_PAYMENT,
            remark=remark
        )

        # 获取商品封面图
        cover_image = db.query(ProductImage).filter(
            and_(ProductImage.product_id == product_id, ProductImage.is_cover == 1)
        ).first()
        if not cover_image:
            cover_image = db.query(ProductImage).filter(
                ProductImage.product_id == product_id
            ).order_by(ProductImage.sort.asc()).first()
        if cover_image:
            new_order.product_image = cover_image.image_url

        db.add(new_order)
        db.flush()

        # 添加订单日志
        order_log = OrderLog(
            order_id=new_order.id,
            operator_id=buyer_id,
            operator_type=1,  # 1-买家
            action="创建订单",
            content=f"买家创建订单，订单号：{order_no}"
        )
        db.add(order_log)

        db.commit()
        db.refresh(new_order)

        return new_order.to_dict()

    @staticmethod
    def get_order_list(db: Session, user_id: int, status: Optional[int] = None,
                       page: int = 1, page_size: int = 20, role: str = "buyer") -> dict:
        """
        获取订单列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 订单状态（可选）
            page: 页码
            page_size: 每页数量
            role: 角色：buyer-买家 seller-卖家

        Returns:
            订单列表
        """
        if role == "seller":
            query = db.query(OrderInfo).filter(OrderInfo.seller_id == user_id)
        else:
            query = db.query(OrderInfo).filter(OrderInfo.buyer_id == user_id)

        if status is not None:
            query = query.filter(OrderInfo.status == status)

        query = query.order_by(desc(OrderInfo.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        orders = query.offset(offset).limit(page_size).all()

        order_list = [order.to_dict() for order in orders]

        return {
            "list": order_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def get_order_detail(db: Session, order_id: int, user_id: int) -> dict:
        """
        获取订单详情

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID

        Returns:
            订单详情
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限查看该订单")

        order_dict = order.to_dict()

        # 获取商品信息
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            order_dict["product"] = product.to_dict()

        # 获取买家信息
        buyer = db.query(User).filter(User.id == order.buyer_id).first()
        if buyer:
            order_dict["buyer"] = {
                "id": buyer.id,
                "username": buyer.username,
                "nickname": buyer.nickname,
                "avatar": buyer.avatar
            }

        # 获取卖家信息
        seller = db.query(User).filter(User.id == order.seller_id).first()
        if seller:
            order_dict["seller"] = {
                "id": seller.id,
                "username": seller.username,
                "nickname": seller.nickname,
                "avatar": seller.avatar
            }

        return order_dict

    @staticmethod
    def pay_order(db: Session, order_id: int, user_id: int, pay_type: int = PayType.OFFLINE) -> dict:
        """
        支付订单

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            pay_type: 支付方式

        Returns:
            支付结果
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查状态
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "订单状态错误")

        # 更新订单状态
        order.status = OrderStatus.PENDING_SHIPMENT
        order.pay_type = pay_type
        order.pay_time = func.now()

        # 添加订单日志
        order_log = OrderLog(
            order_id=order.id,
            operator_id=user_id,
            operator_type=1,  # 1-买家
            action="支付订单",
            content=f"买家支付订单，支付方式：{pay_type}"
        )
        db.add(order_log)

        db.commit()
        db.refresh(order)

        return order.to_dict()

    @staticmethod
    def cancel_order(db: Session, order_id: int, user_id: int, reason: str = None) -> bool:
        """
        取消订单

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            reason: 取消原因

        Returns:
            是否成功
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查状态（只有待付款状态可以取消）
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "当前状态不能取消订单")

        # 更新订单状态
        order.status = OrderStatus.CANCELLED
        order.cancel_time = func.now()
        order.cancel_reason = reason

        # 添加订单日志
        order_log = OrderLog(
            order_id=order.id,
            operator_id=user_id,
            operator_type=1,  # 1-买家
            action="取消订单",
            content=f"买家取消订单，原因：{reason or '无'}"
        )
        db.add(order_log)

        db.commit()

        return True

    @staticmethod
    def ship_order(db: Session, order_id: int, seller_id: int) -> bool:
        """
        发货

        Args:
            db: 数据库会话
            order_id: 订单ID
            seller_id: 卖家ID

        Returns:
            是否成功
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.seller_id != seller_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查状态
        if order.status != OrderStatus.PENDING_SHIPMENT:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "订单状态错误")

        # 更新订单状态
        order.status = OrderStatus.PENDING_RECEIPT
        order.ship_time = func.now()

        # 添加订单日志
        order_log = OrderLog(
            order_id=order.id,
            operator_id=seller_id,
            operator_type=2,  # 2-卖家
            action="发货",
            content="卖家已发货"
        )
        db.add(order_log)

        db.commit()

        return True

    @staticmethod
    def confirm_receipt(db: Session, order_id: int, user_id: int) -> bool:
        """
        确认收货

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查状态
        if order.status != OrderStatus.PENDING_RECEIPT:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "订单状态错误")

        # 更新订单状态
        order.status = OrderStatus.COMPLETED
        order.finish_time = func.now()

        # 更新商品状态为已售
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.status = 1  # 1-已售

        # 添加订单日志
        order_log = OrderLog(
            order_id=order.id,
            operator_id=user_id,
            operator_type=1,  # 1-买家
            action="确认收货",
            content="买家确认收货，订单完成"
        )
        db.add(order_log)

        db.commit()

        return True

    @staticmethod
    def apply_refund(db: Session, order_id: int, user_id: int, reason: str, description: str = None) -> dict:
        """
        申请退款

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            reason: 退款原因
            description: 退款说明

        Returns:
            退款申请信息
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查状态（已完成或待收货可以申请退款）
        if order.status not in [OrderStatus.PENDING_RECEIPT, OrderStatus.COMPLETED]:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "当前状态不能申请退款")

        # 检查是否已有退款申请
        existing_refund = db.query(Refund).filter(
            and_(Refund.order_id == order_id, Refund.status.in_([0, 1, 3]))
        ).first()
        if existing_refund:
            raise BusinessException(ErrorCode.PARAM_ERROR, "已有退款申请正在处理中")

        # 创建退款申请
        refund_no = generate_refund_no()
        new_refund = Refund(
            refund_no=refund_no,
            order_id=order_id,
            user_id=user_id,
            refund_amount=order.pay_amount,
            refund_reason=reason,
            refund_desc=description,
            status=RefundStatus.PENDING
        )

        db.add(new_refund)

        # 更新订单状态
        order.status = OrderStatus.REFUNDING

        # 添加订单日志
        order_log = OrderLog(
            order_id=order.id,
            operator_id=user_id,
            operator_type=1,  # 1-买家
            action="申请退款",
            content=f"买家申请退款，原因：{reason}"
        )
        db.add(order_log)

        db.commit()
        db.refresh(new_refund)

        return new_refund.to_dict()

    @staticmethod
    def get_cart_list(db: Session, user_id: int) -> list:
        """
        获取购物车列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            购物车列表
        """
        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).order_by(desc(Cart.create_time)).all()

        result = []
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.status == 0:  # 只返回上架的商品
                item_dict = item.to_dict()

                # 获取商品信息
                product_dict = product.to_dict()

                # 获取封面图片
                cover_image = db.query(ProductImage).filter(
                    and_(ProductImage.product_id == product.id, ProductImage.is_cover == 1)
                ).first()
                if not cover_image:
                    cover_image = db.query(ProductImage).filter(
                        ProductImage.product_id == product.id
                    ).order_by(ProductImage.sort.asc()).first()
                product_dict["cover_image"] = cover_image.image_url if cover_image else None

                item_dict["product"] = product_dict
                result.append(item_dict)

        return result

    @staticmethod
    def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> dict:
        """
        添加到购物车

        Args:
            db: 数据库会话
            user_id: 用户ID
            product_id: 商品ID
            quantity: 数量

        Returns:
            购物车项
        """
        # 检查商品是否存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        if product.status != 0:
            raise BusinessException(ErrorCode.PRODUCT_OFF_SHELF, "商品已下架")

        # 检查是否已在购物车
        cart_item = db.query(Cart).filter(
            and_(Cart.user_id == user_id, Cart.product_id == product_id)
        ).first()

        if cart_item:
            # 更新数量
            cart_item.quantity += quantity
            db.commit()
            db.refresh(cart_item)
        else:
            # 新建购物车项
            cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)

        return cart_item.to_dict()

    @staticmethod
    def update_cart_item(db: Session, user_id: int, cart_id: int, quantity: int) -> bool:
        """
        更新购物车数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            cart_id: 购物车项ID
            quantity: 数量

        Returns:
            是否成功
        """
        cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart_item:
            raise BusinessException(ErrorCode.NOT_FOUND, "购物车项不存在")

        if cart_item.user_id != user_id:
            raise BusinessException(ErrorCode.FORBIDDEN, "无权限操作")

        if quantity <= 0:
            # 删除购物车项
            db.delete(cart_item)
        else:
            cart_item.quantity = quantity

        db.commit()

        return True

    @staticmethod
    def remove_from_cart(db: Session, user_id: int, cart_ids: list) -> bool:
        """
        从购物车移除

        Args:
            db: 数据库会话
            user_id: 用户ID
            cart_ids: 购物车项ID列表

        Returns:
            是否成功
        """
        db.query(Cart).filter(
            and_(Cart.user_id == user_id, Cart.id.in_(cart_ids))
        ).delete(synchronize_session=False)

        db.commit()

        return True

    @staticmethod
    def create_review(db: Session, order_id: int, user_id: int, rating: int, content: str = None,
                      images: list = None, is_anonymous: int = 0) -> dict:
        """
        创建评价

        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            rating: 评分
            content: 评价内容
            images: 评价图片
            is_anonymous: 是否匿名

        Returns:
            评价信息
        """
        order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()
        if not order:
            raise BusinessException(ErrorCode.ORDER_NOT_FOUND, "订单不存在")

        # 检查权限
        if order.buyer_id != user_id and order.seller_id != user_id:
            raise BusinessException(ErrorCode.ORDER_NOT_BELONG, "无权限操作该订单")

        # 检查订单状态
        if order.status != OrderStatus.COMPLETED:
            raise BusinessException(ErrorCode.ORDER_STATUS_ERROR, "订单未完成，不能评价")

        # 检查是否已评价
        existing_review = db.query(Review).filter(
            and_(Review.order_id == order_id, Review.user_id == user_id)
        ).first()
        if existing_review:
            raise BusinessException(ErrorCode.PARAM_ERROR, "已评价过该订单")

        # 确定评价类型和被评价人
        if order.buyer_id == user_id:
            review_type = 1  # 买家评价卖家
            to_user_id = order.seller_id
        else:
            review_type = 2  # 卖家评价买家
            to_user_id = order.buyer_id

        # 创建评价
        new_review = Review(
            order_id=order_id,
            product_id=order.product_id,
            user_id=user_id,
            to_user_id=to_user_id,
            rating=rating,
            content=content,
            images=images,
            type=review_type,
            is_anonymous=is_anonymous
        )

        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        return new_review.to_dict()

    @staticmethod
    def get_product_reviews(db: Session, product_id: int, page: int = 1, page_size: int = 20) -> dict:
        """
        获取商品评价列表

        Args:
            db: 数据库会话
            product_id: 商品ID
            page: 页码
            page_size: 每页数量

        Returns:
            评价列表
        """
        query = db.query(Review).filter(
            and_(Review.product_id == product_id, Review.status == 0)
        ).order_by(desc(Review.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        reviews = query.offset(offset).limit(page_size).all()

        review_list = []
        for review in reviews:
            review_dict = review.to_dict()

            # 获取评价人信息
            user = db.query(User).filter(User.id == review.user_id).first()
            if user:
                if review.is_anonymous:
                    review_dict["user"] = {
                        "id": user.id,
                        "nickname": "匿名用户",
                        "avatar": None
                    }
                else:
                    review_dict["user"] = {
                        "id": user.id,
                        "nickname": user.nickname or user.username,
                        "avatar": user.avatar
                    }

            review_list.append(review_dict)

        return {
            "list": review_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }
