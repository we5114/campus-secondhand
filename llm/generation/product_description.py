"""
商品描述生成
基于大模型自动生成商品描述
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from typing import Dict, Optional

from utils.llm_utils import LLMClient, PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductDescriptionGenerator:
    """商品描述生成器类"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def generate_description(self, product_info: Dict) -> Optional[str]:
        """
        生成商品描述

        Args:
            product_info: 商品信息字典
                - title: 商品名称
                - category: 商品分类
                - price: 商品价格
                - original_price: 原价
                - condition: 成色
                - trade_type: 交易方式
                - features: 商品特点

        Returns:
            str: 生成的商品描述
        """
        try:
            # 构建提示词
            prompt = PromptTemplate.format_product_description(**product_info)

            # 调用大模型生成
            description = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )

            if description:
                logger.info(f"商品描述生成成功: {product_info.get('title', '')}")
                return description.strip()
            else:
                logger.warning("商品描述生成失败，返回空")
                return None

        except Exception as e:
            logger.error(f"商品描述生成失败: {str(e)}")
            return None

    def generate_title(self, product_info: Dict) -> Optional[str]:
        """
        生成商品标题

        Args:
            product_info: 商品信息

        Returns:
            str: 生成的商品标题
        """
        try:
            prompt = f"""
请根据以下商品信息，生成一个吸引人的商品标题。

商品信息：
- 商品分类：{product_info.get('category', '')}
- 商品价格：{product_info.get('price', '')}元
- 成色：{product_info.get('condition', '')}
- 商品特点：{product_info.get('features', '')}

要求：
1. 标题要简洁明了，不超过30个字
2. 突出商品的核心卖点
3. 适合在二手平台展示
4. 包含关键词便于搜索
"""

            title = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )

            if title:
                # 清理标题（去掉引号等）
                title = title.strip().strip('"').strip("'")
                logger.info(f"商品标题生成成功: {title}")
                return title
            else:
                return None

        except Exception as e:
            logger.error(f"商品标题生成失败: {str(e)}")
            return None

    def generate_tags(self, product_info: Dict) -> Optional[list]:
        """
        生成商品标签

        Args:
            product_info: 商品信息

        Returns:
            list: 生成的商品标签列表
        """
        try:
            prompt = f"""
请根据以下商品信息，生成5-8个适合的商品标签。

商品信息：
- 商品名称：{product_info.get('title', '')}
- 商品分类：{product_info.get('category', '')}
- 商品价格：{product_info.get('price', '')}元
- 成色：{product_info.get('condition', '')}
- 商品特点：{product_info.get('features', '')}

要求：
1. 标签要简洁，每个标签2-6个字
2. 涵盖商品的主要特征
3. 便于用户搜索和分类
4. 用逗号分隔

请直接返回标签列表，不要其他解释。
"""

            tags_text = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_tokens=200
            )

            if tags_text:
                # 解析标签
                tags = [tag.strip() for tag in tags_text.replace('，', ',').split(',') if tag.strip()]
                tags = tags[:8]  # 最多8个标签
                logger.info(f"商品标签生成成功: {tags}")
                return tags
            else:
                return None

        except Exception as e:
            logger.error(f"商品标签生成失败: {str(e)}")
            return None

    def generate_smart_price(self, product_info: Dict, similar_products: list = None) -> Optional[float]:
        """
        智能定价（基于历史数据和相似商品）

        Args:
            product_info: 商品信息
            similar_products: 相似商品列表

        Returns:
            float: 建议价格
        """
        try:
            if similar_products:
                # 基于相似商品价格计算建议价格
                prices = [p.get('price', 0) for p in similar_products if p.get('price')]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    # 根据成色调整
                    condition = product_info.get('condition', 3)  # 默认八成新
                    condition_factor = {
                        1: 0.9,  # 全新
                        2: 0.8,  # 九成新
                        3: 0.7,  # 八成新
                        4: 0.6,  # 七成新
                        5: 0.5   # 其他
                    }.get(condition, 0.7)

                    suggested_price = round(avg_price * condition_factor, 2)
                    logger.info(f"智能定价成功: {suggested_price}元")
                    return suggested_price

            # 如果没有相似商品，使用大模型估算
            prompt = f"""
请根据以下商品信息，估算一个合理的二手价格。

商品信息：
- 商品名称：{product_info.get('title', '')}
- 商品分类：{product_info.get('category', '')}
- 原价：{product_info.get('original_price', '')}元
- 成色：{product_info.get('condition', '')}
- 使用时长：{product_info.get('usage_time', '未知')}

请直接返回建议的价格数字（单位：元），不要其他解释。
"""

            price_text = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=50
            )

            if price_text:
                # 提取数字
                import re
                numbers = re.findall(r'\d+\.?\d*', price_text)
                if numbers:
                    suggested_price = float(numbers[0])
                    logger.info(f"智能定价成功: {suggested_price}元")
                    return suggested_price

            return None

        except Exception as e:
            logger.error(f"智能定价失败: {str(e)}")
            return None

    def generate_full_product_info(self, product_info: Dict) -> Dict:
        """
        生成完整的商品信息（标题、描述、标签、建议价格）

        Args:
            product_info: 商品基本信息

        Returns:
            dict: 完整的商品信息
        """
        result = product_info.copy()

        # 生成标题
        if not result.get('title'):
            title = self.generate_title(product_info)
            if title:
                result['title'] = title

        # 生成描述
        if not result.get('description'):
            description = self.generate_description(product_info)
            if description:
                result['description'] = description

        # 生成标签
        if not result.get('tags'):
            tags = self.generate_tags(product_info)
            if tags:
                result['tags'] = tags

        # 生成建议价格
        if not result.get('suggested_price'):
            suggested_price = self.generate_smart_price(product_info)
            if suggested_price:
                result['suggested_price'] = suggested_price

        logger.info("完整商品信息生成完成")
        return result


if __name__ == "__main__":
    # 测试商品描述生成
    generator = ProductDescriptionGenerator()

    product_info = {
        "title": "iPhone 13 Pro",
        "category": "数码产品",
        "price": 5999,
        "original_price": 7999,
        "condition": "九成新",
        "trade_type": "面交+邮寄",
        "features": "256G, 远峰蓝色, 无磕碰, 电池健康度92%, 原装充电器"
    }

    # 生成描述
    description = generator.generate_description(product_info)
    print(f"商品描述:\n{description}")
    print()

    # 生成标签
    tags = generator.generate_tags(product_info)
    print(f"商品标签: {tags}")
