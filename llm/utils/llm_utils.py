"""
LLM工具类
封装大模型API调用
"""
import os
import json
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMConfig:
    """LLM配置类"""

    # 模型配置
    MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gpt-3.5-turbo")
    API_KEY = os.environ.get("LLM_API_KEY", "")
    API_BASE = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
    TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2000"))
    TOP_P = float(os.environ.get("LLM_TOP_P", "1.0"))

    # 超时配置
    TIMEOUT = int(os.environ.get("LLM_TIMEOUT", "30"))

    # 重试配置
    MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.environ.get("LLM_RETRY_DELAY", "1.0"))


class LLMClient:
    """LLM客户端类"""

    def __init__(self, config=None):
        self.config = config or LLMConfig()
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化LLM客户端"""
        try:
            import openai

            self.client = openai.OpenAI(
                api_key=self.config.API_KEY,
                base_url=self.config.API_BASE,
                timeout=self.config.TIMEOUT
            )
            logger.info("LLM客户端初始化成功")
        except ImportError:
            logger.warning("openai库未安装，使用模拟模式")
            self.client = None
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {str(e)}")
            self.client = None

    def chat_completion(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """
        聊天补全

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}, ...]
            **kwargs: 其他参数

        Returns:
            str: 回复内容
        """
        if not self.client:
            return self._mock_chat_completion(messages)

        try:
            response = self.client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.TEMPERATURE),
                max_tokens=kwargs.get("max_tokens", self.config.MAX_TOKENS),
                top_p=kwargs.get("top_p", self.config.TOP_P)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"聊天补全失败: {str(e)}")
            return None

    def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> Optional[str]:
        """
        生成文本

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            **kwargs: 其他参数

        Returns:
            str: 生成的文本
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(messages, **kwargs)

    def _mock_chat_completion(self, messages: List[Dict]) -> str:
        """
        模拟聊天补全（用于测试）

        Args:
            messages: 消息列表

        Returns:
            str: 模拟回复
        """
        last_message = messages[-1]["content"] if messages else ""

        # 简单的模拟回复
        if "你好" in last_message or "hello" in last_message.lower():
            return "你好！我是校园二手交易平台的智能客服，有什么可以帮您的吗？"
        elif "商品" in last_message:
            return "关于商品的问题，您可以在商品详情页查看详细信息，或者联系卖家咨询。"
        elif "订单" in last_message:
            return "订单相关问题，您可以在'我的订单'页面查看订单状态和详情。"
        elif "退款" in last_message:
            return "如需退款，请在订单详情页申请退款，卖家确认后款项将原路返回。"
        else:
            return "感谢您的咨询，我会尽力为您解答问题。如果问题比较复杂，建议联系人工客服。"

    def stream_chat(self, messages: List[Dict], **kwargs):
        """
        流式聊天

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            str: 流式回复片段
        """
        if not self.client:
            # 模拟流式输出
            response = self._mock_chat_completion(messages)
            for char in response:
                yield char
            return

        try:
            stream = self.client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.TEMPERATURE),
                max_tokens=kwargs.get("max_tokens", self.config.MAX_TOKENS),
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            yield ""


class PromptTemplate:
    """提示词模板类"""

    # 智能客服系统提示
    CUSTOMER_SERVICE_SYSTEM_PROMPT = """
你是校园二手交易平台的智能客服，需要友好、专业地回答用户的问题。

你的职责：
1. 解答用户关于平台使用的问题
2. 帮助用户了解交易流程
3. 提供商品搜索和推荐建议
4. 处理用户投诉和建议

回答要求：
- 语气友好、耐心
- 回答简洁明了
- 如果问题复杂，建议联系人工客服
- 不要泄露用户隐私信息
"""

    # 商品描述生成提示
    PRODUCT_DESCRIPTION_PROMPT = """
请根据以下商品信息，生成一段吸引人的商品描述。

商品信息：
- 商品名称：{title}
- 商品分类：{category}
- 商品价格：{price}元
- 原价：{original_price}元
- 成色：{condition}
- 交易方式：{trade_type}
- 商品特点：{features}

要求：
1. 描述要生动、有吸引力
2. 突出商品的优点和特色
3. 字数控制在200-300字
4. 适合在二手平台展示
"""

    # 内容审核提示
    CONTENT_MODERATION_PROMPT = """
请判断以下内容是否包含违规信息。

内容类型：{content_type}
内容：{content}

违规类型包括：
1. 违法违规内容
2. 色情低俗内容
3. 暴力恐怖内容
4. 虚假诈骗信息
5. 敏感政治内容
6. 其他不良信息

请按以下格式回复：
是否违规：是/否
违规类型：如果违规，说明具体类型
违规原因：简要说明原因
风险等级：低/中/高
"""

    # 情感分析提示
    SENTIMENT_ANALYSIS_PROMPT = """
请分析以下文本的情感倾向。

文本：{text}

请按以下格式回复：
情感倾向：正面/负面/中性
情感分数：0-1之间的数字，1表示最正面，0表示最负面
主要情感：说明具体的情感类型
关键词：提取3-5个情感关键词
"""

    @classmethod
    def format_product_description(cls, **kwargs) -> str:
        """
        格式化商品描述生成提示

        Args:
            **kwargs: 商品信息

        Returns:
            str: 格式化后的提示
        """
        return cls.PRODUCT_DESCRIPTION_PROMPT.format(**kwargs)

    @classmethod
    def format_content_moderation(cls, content_type: str, content: str) -> str:
        """
        格式化内容审核提示

        Args:
            content_type: 内容类型
            content: 内容

        Returns:
            str: 格式化后的提示
        """
        return cls.CONTENT_MODERATION_PROMPT.format(
            content_type=content_type,
            content=content
        )

    @classmethod
    def format_sentiment_analysis(cls, text: str) -> str:
        """
        格式化情感分析提示

        Args:
            text: 文本

        Returns:
            str: 格式化后的提示
        """
        return cls.SENTIMENT_ANALYSIS_PROMPT.format(text=text)


if __name__ == "__main__":
    # 测试LLM客户端
    client = LLMClient()

    # 测试生成文本
    response = client.generate_text("你好，请介绍一下你自己")
    print(f"回复: {response}")

    # 测试提示词模板
    prompt = PromptTemplate.format_product_description(
        title="iPhone 13 Pro",
        category="数码产品",
        price=5999,
        original_price=7999,
        condition="九成新",
        trade_type="面交+邮寄",
        features="256G, 远峰蓝色, 无磕碰, 电池健康度92%"
    )
    print(f"商品描述提示: {prompt[:100]}...")
