"""
商品服务层
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from app.models.product import Product, ProductCategory, ProductImage, ProductCollection
from app.models.user import User
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductQuery
from app.config.constants import ErrorCode, ProductStatus
from app.utils.common import list_to_tree, calculate_page
from app.service.user_service import BusinessException


class ProductService:
    """商品服务类"""

    @staticmethod
    def get_category_tree(db: Session) -> list:
        """
        获取商品分类树

        Args:
            db: 数据库会话

        Returns:
            分类树
        """
        categories = db.query(ProductCategory).filter(
            ProductCategory.status == 0
        ).order_by(ProductCategory.sort.asc()).all()

        # 转换为字典列表
        category_list = [cat.to_dict() for cat in categories]

        # 转换为树形结构
        return list_to_tree(category_list)

    @staticmethod
    def get_product_list(db: Session, query_params: ProductQuery, user_id: Optional[int] = None) -> dict:
        """
        获取商品列表

        Args:
            db: 数据库会话
            query_params: 查询参数
            user_id: 当前用户ID（可选）

        Returns:
            商品列表数据
        """
        query = db.query(Product).filter(Product.status == ProductStatus.ON_SHELF)

        # 分类筛选
        if query_params.category_id:
            # 获取该分类及其子分类
            category = db.query(ProductCategory).filter(
                ProductCategory.id == query_params.category_id
            ).first()
            if category:
                if category.level == 1:
                    # 一级分类，查询所有子分类下的商品
                    sub_categories = db.query(ProductCategory).filter(
                        ProductCategory.parent_id == category.id
                    ).all()
                    category_ids = [cat.id for cat in sub_categories] + [category.id]
                    query = query.filter(Product.category_id.in_(category_ids))
                else:
                    query = query.filter(Product.category_id == query_params.category_id)

        # 关键词搜索
        if query_params.keyword:
            query = query.filter(
                or_(
                    Product.title.like(f"%{query_params.keyword}%"),
                    Product.description.like(f"%{query_params.keyword}%")
                )
            )

        # 价格区间
        if query_params.min_price is not None:
            query = query.filter(Product.price >= query_params.min_price)
        if query_params.max_price is not None:
            query = query.filter(Product.price <= query_params.max_price)

        # 成色筛选
        if query_params.condition:
            query = query.filter(Product.condition == query_params.condition)

        # 卖家筛选
        if query_params.seller_id:
            query = query.filter(Product.seller_id == query_params.seller_id)

        # 排序
        sort_field = query_params.sort_by
        sort_order = query_params.sort_order

        sort_map = {
            "create_time": Product.create_time,
            "price": Product.price,
            "view_count": Product.view_count,
            "favorite_count": Product.favorite_count,
        }

        if sort_field in sort_map:
            if sort_order == "desc":
                query = query.order_by(desc(sort_map[sort_field]))
            else:
                query = query.order_by(asc(sort_map[sort_field]))
        else:
            query = query.order_by(desc(Product.create_time))

        # 置顶优先
        query = query.order_by(desc(Product.is_top))

        # 分页
        total = query.count()
        offset = (query_params.page - 1) * query_params.page_size
        products = query.offset(offset).limit(query_params.page_size).all()

        # 处理商品数据
        product_list = []
        for product in products:
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

            # 获取卖家名称
            seller = db.query(User).filter(User.id == product.seller_id).first()
            product_dict["seller_name"] = seller.nickname or seller.username if seller else None

            # 获取分类名称
            category = db.query(ProductCategory).filter(
                ProductCategory.id == product.category_id
            ).first()
            product_dict["category_name"] = category.name if category else None

            product_list.append(product_dict)

        return {
            "list": product_list,
            "total": total,
            "page": query_params.page,
            "page_size": query_params.page_size,
            "total_pages": calculate_page(total, query_params.page_size)
        }

    @staticmethod
    def get_product_detail(db: Session, product_id: int, user_id: Optional[int] = None) -> dict:
        """
        获取商品详情

        Args:
            db: 数据库会话
            product_id: 商品ID
            user_id: 当前用户ID（可选）

        Returns:
            商品详情
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        # 增加浏览量
        product.view_count += 1
        db.commit()

        product_dict = product.to_dict()

        # 获取商品图片
        images = db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.sort.asc()).all()
        product_dict["images"] = [img.to_dict() for img in images]

        # 获取卖家信息
        seller = db.query(User).filter(User.id == product.seller_id).first()
        if seller:
            product_dict["seller"] = {
                "id": seller.id,
                "username": seller.username,
                "nickname": seller.nickname,
                "avatar": seller.avatar,
                "user_level": seller.user_level,
                "is_real_name": seller.is_real_name
            }

        # 获取分类信息
        category = db.query(ProductCategory).filter(
            ProductCategory.id == product.category_id
        ).first()
        product_dict["category"] = category.to_dict() if category else None

        # 检查是否已收藏
        is_favorite = False
        if user_id:
            favorite = db.query(ProductCollection).filter(
                and_(
                    ProductCollection.user_id == user_id,
                    ProductCollection.product_id == product_id
                )
            ).first()
            is_favorite = favorite is not None
        product_dict["is_favorite"] = is_favorite

        return product_dict

    @staticmethod
    def create_product(db: Session, seller_id: int, product_data: ProductCreate) -> dict:
        """
        发布商品

        Args:
            db: 数据库会话
            seller_id: 卖家ID
            product_data: 商品数据

        Returns:
            创建的商品
        """
        # 检查分类是否存在
        category = db.query(ProductCategory).filter(
            ProductCategory.id == product_data.category_id
        ).first()
        if not category:
            raise BusinessException(ErrorCode.CATEGORY_NOT_FOUND, "分类不存在")

        # 创建商品
        new_product = Product(
            seller_id=seller_id,
            category_id=product_data.category_id,
            title=product_data.title,
            description=product_data.description,
            price=product_data.price,
            original_price=product_data.original_price,
            condition=product_data.condition,
            quality=product_data.quality,
            trade_type=product_data.trade_type,
            location=product_data.location,
            status=ProductStatus.ON_SHELF,  # 直接上架，简化流程
            audit_status=1  # 审核通过
        )

        db.add(new_product)
        db.flush()

        # 添加商品图片
        if product_data.images:
            for i, image_url in enumerate(product_data.images):
                product_image = ProductImage(
                    product_id=new_product.id,
                    image_url=image_url,
                    sort=i,
                    is_cover=1 if i == 0 else 0
                )
                db.add(product_image)

        db.commit()
        db.refresh(new_product)

        return new_product.to_dict()

    @staticmethod
    def update_product(db: Session, product_id: int, seller_id: int, update_data: ProductUpdate) -> dict:
        """
        更新商品

        Args:
            db: 数据库会话
            product_id: 商品ID
            seller_id: 卖家ID
            update_data: 更新数据

        Returns:
            更新后的商品
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        # 检查是否是自己的商品
        if product.seller_id != seller_id:
            raise BusinessException(ErrorCode.PRODUCT_NOT_BELONG, "无权限操作该商品")

        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        images = update_dict.pop("images", None)

        for key, value in update_dict.items():
            if value is not None:
                setattr(product, key, value)

        # 更新图片
        if images is not None:
            # 删除原有图片
            db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()

            # 添加新图片
            for i, image_url in enumerate(images):
                product_image = ProductImage(
                    product_id=product_id,
                    image_url=image_url,
                    sort=i,
                    is_cover=1 if i == 0 else 0
                )
                db.add(product_image)

        db.commit()
        db.refresh(product)

        return product.to_dict()

    @staticmethod
    def delete_product(db: Session, product_id: int, seller_id: int) -> bool:
        """
        删除/下架商品

        Args:
            db: 数据库会话
            product_id: 商品ID
            seller_id: 卖家ID

        Returns:
            是否成功
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        # 检查是否是自己的商品
        if product.seller_id != seller_id:
            raise BusinessException(ErrorCode.PRODUCT_NOT_BELONG, "无权限操作该商品")

        # 下架商品
        product.status = ProductStatus.OFF_SHELF
        db.commit()

        return True

    @staticmethod
    def toggle_favorite(db: Session, user_id: int, product_id: int) -> dict:
        """
        收藏/取消收藏商品

        Args:
            db: 数据库会话
            user_id: 用户ID
            product_id: 商品ID

        Returns:
            操作结果
        """
        # 检查商品是否存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise BusinessException(ErrorCode.PRODUCT_NOT_FOUND, "商品不存在")

        # 检查是否已收藏
        favorite = db.query(ProductCollection).filter(
            and_(
                ProductCollection.user_id == user_id,
                ProductCollection.product_id == product_id
            )
        ).first()

        if favorite:
            # 取消收藏
            db.delete(favorite)
            product.favorite_count = max(0, product.favorite_count - 1)
            is_favorite = False
        else:
            # 添加收藏
            new_favorite = ProductCollection(
                user_id=user_id,
                product_id=product_id
            )
            db.add(new_favorite)
            product.favorite_count += 1
            is_favorite = True

        db.commit()

        return {
            "is_favorite": is_favorite,
            "favorite_count": product.favorite_count
        }

    @staticmethod
    def get_my_favorites(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> dict:
        """
        获取我的收藏列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            收藏列表
        """
        query = db.query(ProductCollection).filter(
            ProductCollection.user_id == user_id
        ).order_by(desc(ProductCollection.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        favorites = query.offset(offset).limit(page_size).all()

        product_list = []
        for fav in favorites:
            product = db.query(Product).filter(Product.id == fav.product_id).first()
            if product:
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

                product_list.append(product_dict)

        return {
            "list": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def get_my_products(db: Session, seller_id: int, page: int = 1, page_size: int = 20, status: Optional[int] = None) -> dict:
        """
        获取我发布的商品

        Args:
            db: 数据库会话
            seller_id: 卖家ID
            page: 页码
            page_size: 每页数量
            status: 商品状态（可选）

        Returns:
            商品列表
        """
        query = db.query(Product).filter(Product.seller_id == seller_id)

        if status is not None:
            query = query.filter(Product.status == status)

        query = query.order_by(desc(Product.create_time))

        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        product_list = []
        for product in products:
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

            product_list.append(product_dict)

        return {
            "list": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": calculate_page(total, page_size)
        }

    @staticmethod
    def get_hot_products(db: Session, limit: int = 10) -> list:
        """
        获取热门商品

        Args:
            db: 数据库会话
            limit: 数量限制

        Returns:
            热门商品列表
        """
        products = db.query(Product).filter(
            Product.status == ProductStatus.ON_SHELF
        ).order_by(
            desc(Product.view_count),
            desc(Product.favorite_count)
        ).limit(limit).all()

        product_list = []
        for product in products:
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

            product_list.append(product_dict)

        return product_list

    @staticmethod
    def get_new_products(db: Session, limit: int = 10) -> list:
        """
        获取最新商品

        Args:
            db: 数据库会话
            limit: 数量限制

        Returns:
            最新商品列表
        """
        products = db.query(Product).filter(
            Product.status == ProductStatus.ON_SHELF
        ).order_by(
            desc(Product.create_time)
        ).limit(limit).all()

        product_list = []
        for product in products:
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

            product_list.append(product_dict)

        return product_list
