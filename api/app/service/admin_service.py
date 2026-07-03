"""
管理服务层
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func

from app.models.user import User, UserRealName
from app.models.product import Product, ProductCategory
from app.models.order import OrderInfo, Refund
from app.config.constants import ErrorCode, UserStatus, ProductStatus, OrderStatus
from app.utils.common import calculate_page
from app.service.user_service import BusinessException


class AdminService:
    """管理服务类"""

    # ==================== 用户管理 ====================

    @staticmethod
    def get_user_list(db: Session, keyword: Optional[str] = None, status: Optional[int] = None,
                      page: int = 1, page_size: int = 20) -> dict:
        """
        获取用户列表

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            status: 用户状态
            page: 页码
            page_size: 每页数量

        Returns:
            用户列表
        """
        query = db.query(User)

        if keyword:
            query = query.filter(
                or_(
                    User.username.like(f"%{keyword}%"),
                    User.phone.like(f"%{keyword}%"),
                    User.nickname.like(f"%{keyword}%")
                )
            )

        if status is not None:
            query = query.filter(User.status == status)

        query = query.order_by(desc(User.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()

        user_list = [user.to_dict() for user in users]

        return {
            "list": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def update_user_status(db: Session, user_id: int, status: int) -> bool:
        """
        更新用户状态

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 状态

        Returns:
            是否成功
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        user.status = status
        db.commit()

        return True

    @staticmethod
    def get_real_name_list(db: Session, status: Optional[int] = None,
                           page: int = 1, page_size: int = 20) -> dict:
        """
        获取实名认证列表

        Args:
            db: 数据库会话
            status: 审核状态
            page: 页码
            page_size: 每页数量

        Returns:
            实名认证列表
        """
        query = db.query(UserRealName)

        if status is not None:
            query = query.filter(UserRealName.status == status)

        query = query.order_by(desc(UserRealName.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        real_names = query.offset(offset).limit(page_size).all()

        result_list = []
        for rn in real_names:
            rn_dict = rn.to_dict()

            # 获取用户信息
            user = db.query(User).filter(User.id == rn.user_id).first()
            if user:
                rn_dict["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "phone": user.phone
                }

            result_list.append(rn_dict)

        return {
            "list": result_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def audit_real_name(db: Session, real_name_id: int, status: int, remark: str = None) -> bool:
        """
        审核实名认证

        Args:
            db: 数据库会话
            real_name_id: 实名认证ID
            status: 审核状态
            remark: 审核备注

        Returns:
            是否成功
        """
        real_name = db.query(UserRealName).filter(UserRealName.id == real_name_id).first()
        if not real_name:
            raise BusinessException(ErrorCode.NOT_FOUND, "实名认证申请不存在")

        real_name.status = status
        real_name.audit_remark = remark
        real_name.audit_time = func.now()

        # 如果审核通过，更新用户实名认证状态
        if status == 1:
            user = db.query(User).filter(User.id == real_name.user_id).first()
            if user:
                user.is_real_name = 1

        db.commit()

        return True

    # ==================== 商品管理 ====================

    @staticmethod
    def get_product_list(db: Session, keyword: Optional[str] = None, status: Optional[int] = None,
                         category_id: Optional[int] = None, page: int = 1, page_size: int = 20) -> dict:
        """
        获取商品列表

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            status: 商品状态
            category_id: 分类ID
            page: 页码
            page_size: 每页数量

        Returns:
            商品列表
        """
        query = db.query(Product)

        if keyword:
            query = query.filter(
                or_(
                    Product.title.like(f"%{keyword}%"),
                    Product.description.like(f"%{keyword}%")
                )
            )

        if status is not None:
            query = query.filter(Product.status == status)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        query = query.order_by(desc(Product.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        product_list = [product.to_dict() for product in products]

        return {
            "list": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def update_product_status(db: Session, product_id: int, status: int) -> bool:
        """
        更新商品状态

        Args:
            db: 数据库会话
            product_id: 商品ID
            status: 状态

        Returns:
            是否成功
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        product.status = status
        db.commit()

        return True

    @staticmethod
    def set_product_recommend(db: Session, product_id: int, is_recommend: int) -> bool:
        """
        设置商品推荐

        Args:
            db: 数据库会话
            product_id: 商品ID
            is_recommend: 是否推荐

        Returns:
            是否成功
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        product.is_recommend = is_recommend
        db.commit()

        return True

    # ==================== 订单管理 ====================

    @staticmethod
    def get_order_list(db: Session, keyword: Optional[str] = None, status: Optional[int] = None,
                       page: int = 1, page_size: int = 20) -> dict:
        """
        获取订单列表

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            status: 订单状态
            page: 页码
            page_size: 每页数量

        Returns:
            订单列表
        """
        query = db.query(OrderInfo)

        if keyword:
            query = query.filter(
                or_(
                    OrderInfo.order_no.like(f"%{keyword}%"),
                    OrderInfo.product_title.like(f"%{keyword}%")
                )
            )

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

    # ==================== 数据统计 ====================

    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """
        获取仪表盘统计数据

        Args:
            db: 数据库会话

        Returns:
            统计数据
        """
        # 用户总数
        total_users = db.query(User).count()

        # 今日新增用户
        from datetime import date
        today = date.today()
        today_users = db.query(User).filter(
            func.date(User.create_time) == today
        ).count()

        # 商品总数
        total_products = db.query(Product).count()

        # 在售商品数
        on_shelf_products = db.query(Product).filter(
            Product.status == ProductStatus.ON_SHELF
        ).count()

        # 订单总数
        total_orders = db.query(OrderInfo).count()

        # 今日订单数
        today_orders = db.query(OrderInfo).filter(
            func.date(OrderInfo.create_time) == today
        ).count()

        # 交易总额
        total_amount = db.query(
            func.sum(OrderInfo.pay_amount)
        ).filter(
            OrderInfo.status == OrderStatus.COMPLETED
        ).scalar() or 0

        # 待审核实名认证
        pending_real_name = db.query(UserRealName).filter(
            UserRealName.status == 0
        ).count()

        return {
            "users": {
                "total": total_users,
                "today_new": today_users
            },
            "products": {
                "total": total_products,
                "on_shelf": on_shelf_products
            },
            "orders": {
                "total": total_orders,
                "today_new": today_orders,
                "total_amount": float(total_amount)
            },
            "pending": {
                "real_name": pending_real_name
            }
        }

    @staticmethod
    def get_sales_trend(db: Session, days: int = 7) -> dict:
        """
        获取销售趋势数据

        Args:
            db: 数据库会话
            days: 天数

        Returns:
            销售趋势数据
        """
        # 这里简化实现，实际项目中应该按日期分组统计
        # 暂时返回模拟数据
        dates = []
        order_counts = []
        amounts = []

        from datetime import datetime, timedelta
        for i in range(days - 1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)

            # 模拟数据
            order_counts.append(50 + i * 5)
            amounts.append(5000 + i * 200)

        return {
            "dates": dates,
            "order_counts": order_counts,
            "amounts": amounts
        }

    @staticmethod
    def get_category_stats(db: Session) -> list:
        """
        获取分类统计数据

        Args:
            db: 数据库会话

        Returns:
            分类统计列表
        """
        categories = db.query(ProductCategory).filter(
            ProductCategory.level == 1
        ).all()

        result = []
        for cat in categories:
            # 获取该分类下的商品数
            product_count = db.query(Product).filter(
                Product.category_id == cat.id
            ).count()

            result.append({
                "category_id": cat.id,
                "category_name": cat.name,
                "product_count": product_count
            })

        return result
