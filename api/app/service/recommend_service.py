"""
推荐服务层
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.product import Product, ProductImage, ProductCategory
from app.models.user import User
from app.models.order import OrderInfo
from app.config.constants import ProductStatus
from app.utils.common import calculate_page


class RecommendService:
    """推荐服务类"""

    @staticmethod
    def get_home_recommend(db: Session, user_id: Optional[int] = None, limit: int = 20) -> dict:
        """
        获取首页推荐商品

        Args:
            db: 数据库会话
            user_id: 用户ID（可选，用于个性化推荐）
            limit: 推荐数量

        Returns:
            推荐商品列表
        """
        # 推荐策略：混合推荐
        # 1. 热门商品（40%）
        # 2. 最新商品（30%）
        # 3. 推荐商品（30%）

        hot_count = int(limit * 0.4)
        new_count = int(limit * 0.3)
        recommend_count = limit - hot_count - new_count

        # 获取热门商品
        hot_products = RecommendService._get_hot_products(db, hot_count)

        # 获取最新商品
        new_products = RecommendService._get_new_products(db, new_count)

        # 获取推荐商品
        recommend_products = RecommendService._get_recommend_products(db, recommend_count)

        # 合并并去重
        product_ids = set()
        all_products = []

        for product in hot_products + new_products + recommend_products:
            if product["id"] not in product_ids:
                product_ids.add(product["id"])
                all_products.append(product)
                if len(all_products) >= limit:
                    break

        return {
            "list": all_products,
            "total": len(all_products)
        }

    @staticmethod
    def get_similar_products(db: Session, product_id: int, limit: int = 10) -> list:
        """
        获取相似商品推荐

        Args:
            db: 数据库会话
            product_id: 商品ID
            limit: 推荐数量

        Returns:
            相似商品列表
        """
        # 获取当前商品信息
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []

        # 基于分类的相似推荐
        similar_products = db.query(Product).filter(
            and_(
                Product.category_id == product.category_id,
                Product.id != product_id,
                Product.status == ProductStatus.ON_SHELF
            )
        ).order_by(
            desc(Product.view_count),
            desc(Product.favorite_count)
        ).limit(limit).all()

        result = []
        for p in similar_products:
            product_dict = p.to_dict()

            # 获取封面图片
            cover_image = db.query(ProductImage).filter(
                and_(ProductImage.product_id == p.id, ProductImage.is_cover == 1)
            ).first()
            if not cover_image:
                cover_image = db.query(ProductImage).filter(
                    ProductImage.product_id == p.id
                ).order_by(ProductImage.sort.asc()).first()
            product_dict["cover_image"] = cover_image.image_url if cover_image else None

            result.append(product_dict)

        return result

    @staticmethod
    def get_personalized_recommend(db: Session, user_id: int, limit: int = 20) -> list:
        """
        获取个性化推荐

        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 推荐数量

        Returns:
            个性化推荐列表
        """
        # 简单的个性化推荐策略：
        # 1. 基于用户浏览历史的分类偏好
        # 2. 基于用户收藏的分类偏好
        # 3. 基于用户购买的分类偏好

        # 获取用户购买过的商品分类
        orders = db.query(OrderInfo).filter(
            and_(
                OrderInfo.buyer_id == user_id,
                OrderInfo.status == 3  # 已完成
            )
        ).all()

        category_ids = set()
        for order in orders:
            product = db.query(Product).filter(Product.id == order.product_id).first()
            if product:
                category_ids.add(product.category_id)

        # 如果有用户偏好分类，优先推荐这些分类的商品
        if category_ids:
            products = db.query(Product).filter(
                and_(
                    Product.category_id.in_(list(category_ids)),
                    Product.status == ProductStatus.ON_SHELF,
                    Product.seller_id != user_id  # 不推荐自己的商品
                )
            ).order_by(
                desc(Product.view_count),
                desc(Product.create_time)
            ).limit(limit).all()
        else:
            # 没有偏好，返回热门商品
            products = RecommendService._get_hot_products(db, limit)
            return products

        result = []
        for p in products:
            product_dict = p.to_dict()

            # 获取封面图片
            cover_image = db.query(ProductImage).filter(
                and_(ProductImage.product_id == p.id, ProductImage.is_cover == 1)
            ).first()
            if not cover_image:
                cover_image = db.query(ProductImage).filter(
                    ProductImage.product_id == p.id
                ).order_by(ProductImage.sort.asc()).first()
            product_dict["cover_image"] = cover_image.image_url if cover_image else None

            result.append(product_dict)

        return result

    @staticmethod
    def _get_hot_products(db: Session, limit: int) -> list:
        """获取热门商品"""
        products = db.query(Product).filter(
            Product.status == ProductStatus.ON_SHELF
        ).order_by(
            desc(Product.view_count),
            desc(Product.favorite_count)
        ).limit(limit).all()

        result = []
        for p in products:
            product_dict = p.to_dict()

            # 获取封面图片
            cover_image = db.query(ProductImage).filter(
                and_(ProductImage.product_id == p.id, ProductImage.is_cover == 1)
            ).first()
            if not cover_image:
                cover_image = db.query(ProductImage).filter(
                    ProductImage.product_id == p.id
                ).order_by(ProductImage.sort.asc()).first()
            product_dict["cover_image"] = cover_image.image_url if cover_image else None

            result.append(product_dict)

        return result

    @staticmethod
    def _get_new_products(db: Session, limit: int) -> list:
        """获取最新商品"""
        products = db.query(Product).filter(
            Product.status == ProductStatus.ON_SHELF
        ).order_by(
            desc(Product.create_time)
        ).limit(limit).all()

        result = []
        for p in products:
            product_dict = p.to_dict()

            # 获取封面图片
            cover_image = db.query(ProductImage).filter(
                and_(ProductImage.product_id == p.id, ProductImage.is_cover == 1)
            ).first()
            if not cover_image:
                cover_image = db.query(ProductImage).filter(
                    ProductImage.product_id == p.id
                ).order_by(ProductImage.sort.asc()).first()
            product_dict["cover_image"] = cover_image.image_url if cover_image else None

            result.append(product_dict)

        return result

    @staticmethod
    def _get_recommend_products(db: Session, limit: int) -> list:
        """获取推荐商品（管理员推荐）"""
        products = db.query(Product).filter(
            and_(
                Product.status == ProductStatus.ON_SHELF,
                Product.is_recommend == 1
            )
        ).order_by(
            desc(Product.is_top),
            desc(Product.create_time)
        ).limit(limit).all()

        # 如果推荐商品不够，用热门商品补充
        if len(products) < limit:
            hot_products = RecommendService._get_hot_products(db, limit - len(products))
            products_dict_list = [p.to_dict() for p in products]
            return products_dict_list + hot_products

        result = []
        for p in products:
            product_dict = p.to_dict()

            # 获取封面图片
            cover_image = db.query(ProductImage).filter(
                and_(ProductImage.product_id == p.id, ProductImage.is_cover == 1)
            ).first()
            if not cover_image:
                cover_image = db.query(ProductImage).filter(
                    ProductImage.product_id == p.id
                ).order_by(ProductImage.sort.asc()).first()
            product_dict["cover_image"] = cover_image.image_url if cover_image else None

            result.append(product_dict)

        return result
