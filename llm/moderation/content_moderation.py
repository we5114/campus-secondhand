"""
内容审核
基于大模型的内容安全审核
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import logging
from typing import Dict, Optional, List

from utils.llm_utils import LLMClient, PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentModerator:
    """内容审核类"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()
        self.sensitive_words = self._load_sensitive_words()

    def _load_sensitive_words(self) -> List[str]:
        """
        加载敏感词库

        Returns:
            list: 敏感词列表
        """
        # 这里简化处理，实际项目中应该从文件或数据库加载
        return [
            # 违法违规
            "赌博", "博彩", "色情", "毒品", "枪支",
            # 政治敏感
            "六四", "法轮功",
            # 诈骗相关
            "刷单", "返利", "兼职", "赚钱",
            # 其他
            "代考", "代写", "办证"
        ]

    def check_sensitive_words(self, content: str) -> Dict:
        """
        敏感词检测

        Args:
            content: 内容

        Returns:
            dict: 检测结果
        """
        found_words = []
        content_lower = content.lower()

        for word in self.sensitive_words:
            if word.lower() in content_lower:
                found_words.append(word)

        result = {
            "has_sensitive": len(found_words) > 0,
            "sensitive_words": found_words,
            "risk_level": "high" if len(found_words) >= 3 else ("medium" if len(found_words) >= 1 else "low")
        }

        return result

    def check_with_llm(self, content: str, content_type: str = "text") -> Dict:
        """
        使用大模型进行内容审核

        Args:
            content: 内容
            content_type: 内容类型

        Returns:
            dict: 审核结果
        """
        try:
            # 构建提示词
            prompt = PromptTemplate.format_content_moderation(
                content_type=content_type,
                content=content
            )

            # 调用大模型
            response = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=200
            )

            if not response:
                return {
                    "is_violation": False,
                    "violation_type": "",
                    "violation_reason": "",
                    "risk_level": "low",
                    "check_method": "sensitive_words"
                }

            # 解析结果
            result = self._parse_moderation_result(response)
            result["check_method"] = "llm"

            return result

        except Exception as e:
            logger.error(f"大模型内容审核失败: {str(e)}")
            return {
                "is_violation": False,
                "violation_type": "",
                "violation_reason": "",
                "risk_level": "low",
                "check_method": "fallback"
            }

    def _parse_moderation_result(self, response: str) -> Dict:
        """
        解析审核结果

        Args:
            response: 大模型回复

        Returns:
            dict: 解析后的结果
        """
        result = {
            "is_violation": False,
            "violation_type": "",
            "violation_reason": "",
            "risk_level": "low"
        }

        # 解析是否违规
        if "是否违规：是" in response or "是否违规: 是" in response:
            result["is_violation"] = True
        elif "是否违规：否" in response or "是否违规: 否" in response:
            result["is_violation"] = False

        # 解析违规类型
        type_match = re.search(r'违规类型[：:]\s*(.+)', response)
        if type_match:
            result["violation_type"] = type_match.group(1).strip()

        # 解析违规原因
        reason_match = re.search(r'违规原因[：:]\s*(.+)', response)
        if reason_match:
            result["violation_reason"] = reason_match.group(1).strip()

        # 解析风险等级
        level_match = re.search(r'风险等级[：:]\s*(.+)', response)
        if level_match:
            result["risk_level"] = level_match.group(1).strip().lower()

        return result

    def moderate_content(self, content: str, content_type: str = "text") -> Dict:
        """
        综合内容审核（敏感词 + 大模型）

        Args:
            content: 内容
            content_type: 内容类型

        Returns:
            dict: 审核结果
        """
        # 1. 先进行敏感词检测
        sensitive_result = self.check_sensitive_words(content)

        # 如果敏感词检测到高风险，直接返回
        if sensitive_result["risk_level"] == "high":
            return {
                "is_violation": True,
                "violation_type": "敏感词违规",
                "violation_reason": f"包含敏感词：{', '.join(sensitive_result['sensitive_words'])}",
                "risk_level": "high",
                "check_method": "sensitive_words",
                "sensitive_words": sensitive_result["sensitive_words"]
            }

        # 2. 如果有敏感词但风险不高，或者没有敏感词，使用大模型进一步审核
        llm_result = self.check_with_llm(content, content_type)

        # 合并结果
        final_result = llm_result.copy()
        if sensitive_result["has_sensitive"]:
            final_result["sensitive_words"] = sensitive_result["sensitive_words"]
            # 如果大模型也认为违规，升级风险等级
            if llm_result["is_violation"]:
                final_result["risk_level"] = "high"

        logger.info(f"内容审核完成，违规: {final_result['is_violation']}, 风险等级: {final_result['risk_level']}")
        return final_result

    def moderate_product(self, product_info: Dict) -> Dict:
        """
        审核商品内容

        Args:
            product_info: 商品信息

        Returns:
            dict: 审核结果
        """
        # 组合商品内容
        content = f"""
商品标题：{product_info.get('title', '')}
商品描述：{product_info.get('description', '')}
商品分类：{product_info.get('category', '')}
价格：{product_info.get('price', '')}
        """.strip()

        result = self.moderate_content(content, content_type="product")

        # 额外检查价格是否合理
        price = product_info.get('price', 0)
        if price and price <= 0:
            result["is_violation"] = True
            result["violation_type"] = "价格异常"
            result["violation_reason"] = "商品价格异常"
            result["risk_level"] = "medium"

        return result

    def moderate_comment(self, comment: str) -> Dict:
        """
        审核评论内容

        Args:
            comment: 评论内容

        Returns:
            dict: 审核结果
        """
        result = self.moderate_content(comment, content_type="comment")

        # 额外检查评论长度
        if len(comment.strip()) < 2:
            result["is_violation"] = True
            result["violation_type"] = "内容过短"
            result["violation_reason"] = "评论内容过短"
            result["risk_level"] = "low"

        return result

    def moderate_user_info(self, user_info: Dict) -> Dict:
        """
        审核用户信息

        Args:
            user_info: 用户信息

        Returns:
            dict: 审核结果
        """
        # 组合用户信息
        content = f"""
用户名：{user_info.get('username', '')}
昵称：{user_info.get('nickname', '')}
个人简介：{user_info.get('bio', '')}
        """.strip()

        return self.moderate_content(content, content_type="user_info")


class SentimentAnalyzer:
    """情感分析类"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()

    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析文本情感

        Args:
            text: 文本

        Returns:
            dict: 情感分析结果
        """
        try:
            # 构建提示词
            prompt = PromptTemplate.format_sentiment_analysis(text=text)

            # 调用大模型
            response = self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=200
            )

            if not response:
                return {
                    "sentiment": "neutral",
                    "score": 0.5,
                    "main_emotion": "",
                    "keywords": []
                }

            # 解析结果
            result = self._parse_sentiment_result(response)
            return result

        except Exception as e:
            logger.error(f"情感分析失败: {str(e)}")
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "main_emotion": "",
                "keywords": []
            }

    def _parse_sentiment_result(self, response: str) -> Dict:
        """
        解析情感分析结果

        Args:
            response: 大模型回复

        Returns:
            dict: 解析后的结果
        """
        result = {
            "sentiment": "neutral",
            "score": 0.5,
            "main_emotion": "",
            "keywords": []
        }

        # 解析情感倾向
        if "正面" in response:
            result["sentiment"] = "positive"
        elif "负面" in response:
            result["sentiment"] = "negative"
        elif "中性" in response:
            result["sentiment"] = "neutral"

        # 解析情感分数
        score_match = re.search(r'情感分数[：:]\s*([\d.]+)', response)
        if score_match:
            try:
                result["score"] = float(score_match.group(1))
            except ValueError:
                pass

        # 解析主要情感
        emotion_match = re.search(r'主要情感[：:]\s*(.+)', response)
        if emotion_match:
            result["main_emotion"] = emotion_match.group(1).strip()

        # 解析关键词
        keywords_match = re.search(r'关键词[：:]\s*(.+)', response)
        if keywords_match:
            keywords_str = keywords_match.group(1).strip()
            result["keywords"] = [k.strip() for k in re.split(r'[,，、]', keywords_str) if k.strip()]

        return result

    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """
        批量情感分析

        Args:
            texts: 文本列表

        Returns:
            list: 分析结果列表
        """
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        return results


if __name__ == "__main__":
    # 测试内容审核
    moderator = ContentModerator()

    # 测试敏感词检测
    result = moderator.check_sensitive_words("这是一个正常的商品")
    print(f"敏感词检测: {result}")

    # 测试商品审核
    product_info = {
        "title": "iPhone 13 Pro 九成新",
        "description": "自用手机，无磕碰，功能正常",
        "category": "数码产品",
        "price": 5999
    }
    result = moderator.moderate_product(product_info)
    print(f"商品审核: {result}")

    # 测试情感分析
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_sentiment("这个商品质量很好，卖家服务也很周到，非常满意！")
    print(f"情感分析: {result}")
