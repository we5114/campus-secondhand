"""
大模型服务层
"""
from typing import Optional, List
import httpx
import json

from app.config.settings import settings
from app.config.constants import ErrorCode
from app.service.user_service import BusinessException


class LLMService:
    """大模型服务类"""

    @staticmethod
    async def chat_with_ai(message: str, history: Optional[list] = None,
                           system_prompt: Optional[str] = None) -> dict:
        """
        与AI对话（智能客服）

        Args:
            message: 用户消息
            history: 对话历史
            system_prompt: 系统提示词

        Returns:
            AI回复
        """
        # 默认系统提示词
        if not system_prompt:
            system_prompt = """你是校园二手交易平台的智能客服助手。
你的职责是：
1. 解答用户关于平台使用的问题
2. 帮助用户查找商品
3. 提供交易安全建议
4. 引导用户正确使用平台功能

请用友好、专业的语气回答用户问题。
如果遇到无法回答的问题，请引导用户联系人工客服。"""

        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        try:
            # 调用大模型API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_message = result["choices"][0]["message"]["content"]
                    return {
                        "content": ai_message,
                        "role": "assistant"
                    }
                else:
                    raise BusinessException(ErrorCode.LLM_SERVICE_ERROR, "大模型服务异常")

        except httpx.RequestError:
            # 如果大模型服务不可用，返回默认回复
            return {
                "content": "抱歉，我现在暂时无法回答您的问题。请稍后再试，或者联系人工客服获取帮助。",
                "role": "assistant"
            }

    @staticmethod
    async def generate_product_description(title: str, category: str,
                                           condition: str, price: float,
                                           original_price: Optional[float] = None,
                                           features: Optional[List[str]] = None) -> dict:
        """
        生成商品描述

        Args:
            title: 商品标题
            category: 商品分类
            condition: 商品成色
            price: 售价
            original_price: 原价
            features: 商品特点列表

        Returns:
            生成的商品描述
        """
        # 构建提示词
        prompt = f"""请帮我生成一段校园二手商品的销售描述。

商品信息：
- 标题：{title}
- 分类：{category}
- 成色：{condition}
- 售价：{price}元
"""

        if original_price:
            prompt += f"- 原价：{original_price}元\n"

        if features:
            prompt += f"- 特点：{', '.join(features)}\n"

        prompt += """
要求：
1. 语言生动有吸引力，但要真实可信
2. 突出商品的优点和性价比
3. 适合大学生群体的语言风格
4. 字数在200-300字左右
5. 分点列出商品亮点
6. 最后加上温馨提示，如"支持面交验货"等

请直接输出商品描述内容。"""

        try:
            # 调用大模型API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 1000
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    description = result["choices"][0]["message"]["content"]
                    return {
                        "description": description.strip()
                    }
                else:
                    # 返回默认模板
                    default_desc = LLMService._get_default_product_description(
                        title, category, condition, price, original_price, features
                    )
                    return {"description": default_desc}

        except httpx.RequestError:
            # 如果大模型服务不可用，返回默认模板
            default_desc = LLMService._get_default_product_description(
                title, category, condition, price, original_price, features
            )
            return {"description": default_desc}

    @staticmethod
    def _get_default_product_description(title: str, category: str, condition: str,
                                         price: float, original_price: Optional[float] = None,
                                         features: Optional[List[str]] = None) -> str:
        """生成默认商品描述"""
        desc = f"【{title}】\n\n"
        desc += f"📦 分类：{category}\n"
        desc += f"✨ 成色：{condition}\n"
        desc += f"💰 售价：{price}元\n"

        if original_price and original_price > price:
            discount = int((1 - price / original_price) * 100)
            desc += f"🏷️ 原价：{original_price}元（省{discount}%）\n"

        if features:
            desc += "\n🌟 商品亮点：\n"
            for i, feature in enumerate(features, 1):
                desc += f"{i}. {feature}\n"

        desc += "\n💬 温馨提示：\n"
        desc += "- 支持校园里面交验货\n"
        desc += "- 商品如实描述，所见即所得\n"
        desc += "- 如有问题欢迎随时咨询\n"

        return desc

    @staticmethod
    async def content_moderation(content: str) -> dict:
        """
        内容审核

        Args:
            content: 待审核内容

        Returns:
            审核结果
        """
        # 简单的敏感词过滤（实际项目中应该使用专门的内容审核服务）
        sensitive_words = [
            "赌博", "色情", "毒品", "枪支", "爆炸物",
            "诈骗", "传销", "非法集资", "假币",
            "违禁品", "走私", "假货", "盗版"
        ]

        found_words = []
        for word in sensitive_words:
            if word in content:
                found_words.append(word)

        is_safe = len(found_words) == 0
        risk_level = "safe" if is_safe else "high"

        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "sensitive_words": found_words,
            "suggestion": "内容正常，可以发布" if is_safe else "内容包含敏感词，请修改后再发布"
        }

    @staticmethod
    async def smart_pricing(category: str, condition: str, original_price: float,
                            age_months: int = 0, brand: Optional[str] = None) -> dict:
        """
        智能定价建议

        Args:
            category: 商品分类
            condition: 成色
            original_price: 原价
            age_months: 使用时长（月）
            brand: 品牌

        Returns:
            定价建议
        """
        # 基础折扣率（基于成色）
        condition_discount = {
            "全新": 0.9,
            "九成新": 0.8,
            "八成新": 0.7,
            "七成新": 0.6,
            "其他": 0.5
        }

        base_rate = condition_discount.get(condition, 0.7)

        # 使用时长折旧（每月折旧1%）
        age_depreciation = min(age_months * 0.01, 0.3)
        final_rate = max(base_rate - age_depreciation, 0.3)

        # 品牌溢价
        brand_bonus = 0
        if brand and brand.lower() in ["apple", "huawei", "xiaomi", "sony", "canon"]:
            brand_bonus = 0.05

        suggested_price = original_price * (final_rate + brand_bonus)

        # 价格区间
        min_price = suggested_price * 0.9
        max_price = suggested_price * 1.1

        return {
            "suggested_price": round(suggested_price, 2),
            "price_range": {
                "min": round(min_price, 2),
                "max": round(max_price, 2)
            },
            "factors": {
                "condition_rate": base_rate,
                "age_depreciation": age_depreciation,
                "brand_bonus": brand_bonus
            },
            "tips": [
                f"基于{condition}成色，建议折扣率约{int(final_rate*100)}%",
                f"使用{age_months}个月，折旧约{int(age_depreciation*100)}%",
                "可根据市场行情适当调整价格",
                "定价合理有助于快速成交"
            ]
        }

    @staticmethod
    async def sentiment_analysis(text: str) -> dict:
        """
        情感分析

        Args:
            text: 待分析文本

        Returns:
            情感分析结果
        """
        # 简单的情感关键词分析（实际项目中应该使用专门的情感分析模型）
        positive_words = [
            "好", "棒", "赞", "喜欢", "满意", "优秀", "不错",
            "完美", "超值", "推荐", "开心", "高兴", "感谢",
            "正品", "新", "快", "方便", "划算"
        ]

        negative_words = [
            "差", "烂", "坏", "失望", "不满", "糟糕", "垃圾",
            "骗人", "假货", "破旧", "慢", "贵", "坑", "后悔",
            "问题", "故障", "损坏", "退货"
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total = positive_count + negative_count
        if total == 0:
            sentiment = "neutral"
            score = 0.5
        else:
            score = positive_count / total
            if score > 0.6:
                sentiment = "positive"
            elif score < 0.4:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "confidence": min(total * 0.1, 0.9)
        }
