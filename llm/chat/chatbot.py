"""
智能客服对话系统
基于大模型的智能客服
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from utils.llm_utils import LLMClient, PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Chatbot:
    """智能客服类"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient()
        self.conversation_history = {}  # 用户对话历史
        self.max_history = 10  # 最大历史消息数

    def get_response(self, user_id: str, message: str, context: Dict = None) -> str:
        """
        获取客服回复

        Args:
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息

        Returns:
            str: 回复内容
        """
        # 获取或初始化对话历史
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        history = self.conversation_history[user_id]

        # 构建消息列表
        messages = []

        # 添加系统提示
        system_prompt = self._build_system_prompt(context)
        messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        messages.extend(history[-self.max_history:])

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        # 调用LLM获取回复
        response = self.llm_client.chat_completion(messages)

        if response:
            # 更新对话历史
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

            # 限制历史长度
            if len(history) > self.max_history * 2:
                self.conversation_history[user_id] = history[-self.max_history * 2:]

        return response or "抱歉，我暂时无法回答您的问题，请稍后再试。"

    def _build_system_prompt(self, context: Dict = None) -> str:
        """
        构建系统提示

        Args:
            context: 上下文信息

        Returns:
            str: 系统提示
        """
        base_prompt = PromptTemplate.CUSTOMER_SERVICE_SYSTEM_PROMPT

        # 添加上下文信息
        if context:
            context_info = "\n\n当前上下文信息："
            if context.get("user_name"):
                context_info += f"\n- 用户昵称：{context['user_name']}"
            if context.get("user_level"):
                context_info += f"\n- 用户等级：{context['user_level']}"
            if context.get("current_page"):
                context_info += f"\n- 当前页面：{context['current_page']}"
            if context.get("product_info"):
                context_info += f"\n- 浏览商品：{context['product_info']}"

            base_prompt += context_info

        return base_prompt

    def stream_response(self, user_id: str, message: str, context: Dict = None):
        """
        流式获取客服回复

        Args:
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息

        Yields:
            str: 回复片段
        """
        # 获取或初始化对话历史
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        history = self.conversation_history[user_id]

        # 构建消息列表
        messages = []

        # 添加系统提示
        system_prompt = self._build_system_prompt(context)
        messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        messages.extend(history[-self.max_history:])

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        # 流式获取回复
        full_response = ""
        for chunk in self.llm_client.stream_chat(messages):
            full_response += chunk
            yield chunk

        # 更新对话历史
        if full_response:
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})

            # 限制历史长度
            if len(history) > self.max_history * 2:
                self.conversation_history[user_id] = history[-self.max_history * 2:]

    def clear_history(self, user_id: str):
        """
        清除用户对话历史

        Args:
            user_id: 用户ID
        """
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"清除用户 {user_id} 的对话历史")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """
        获取用户对话历史

        Args:
            user_id: 用户ID

        Returns:
            list: 对话历史
        """
        return self.conversation_history.get(user_id, [])


class FAQChatbot(Chatbot):
    """基于FAQ的智能客服（带知识库）"""

    def __init__(self, llm_client=None, faq_data=None):
        super().__init__(llm_client)
        self.faq_data = faq_data or self._load_default_faq()

    def _load_default_faq(self) -> List[Dict]:
        """
        加载默认FAQ数据

        Returns:
            list: FAQ列表
        """
        return [
            {
                "question": "如何发布商品？",
                "answer": "您可以点击首页的'发布商品'按钮，填写商品信息并上传图片后即可发布。发布后需要通过审核才能上架。",
                "keywords": ["发布", "商品", "上架", "发布商品"]
            },
            {
                "question": "如何购买商品？",
                "answer": "您可以在商品详情页点击'立即购买'或'加入购物车'，然后按照提示完成支付即可。",
                "keywords": ["购买", "下单", "买", "购物"]
            },
            {
                "question": "如何申请退款？",
                "answer": "您可以在订单详情页点击'申请退款'，填写退款原因后提交申请。卖家确认后款项将原路返回。",
                "keywords": ["退款", "退货", "退钱", "申请退款"]
            },
            {
                "question": "如何联系卖家？",
                "answer": "您可以在商品详情页点击'联系卖家'按钮，进入聊天页面与卖家沟通。",
                "keywords": ["联系", "卖家", "聊天", "咨询"]
            },
            {
                "question": "商品多久能发货？",
                "answer": "一般情况下，卖家会在24小时内发货。如果选择面交，可以与卖家协商具体时间和地点。",
                "keywords": ["发货", "物流", "快递", "时间"]
            },
            {
                "question": "平台收手续费吗？",
                "answer": "目前平台不收取任何手续费，所有交易都是免费的。",
                "keywords": ["手续费", "费用", "收费", "佣金"]
            },
            {
                "question": "如何实名认证？",
                "answer": "您可以在'我的'页面点击'实名认证'，上传身份证照片并填写相关信息，审核通过后即可完成认证。",
                "keywords": ["实名", "认证", "身份证", "实名认证"]
            },
            {
                "question": "忘记密码怎么办？",
                "answer": "您可以在登录页面点击'忘记密码'，通过手机号或邮箱重置密码。",
                "keywords": ["密码", "忘记", "重置", "找回密码"]
            }
        ]

    def find_faq(self, question: str) -> Optional[Dict]:
        """
        查找匹配的FAQ

        Args:
            question: 用户问题

        Returns:
            dict: 匹配的FAQ
        """
        # 简单的关键词匹配
        question_lower = question.lower()

        best_match = None
        max_keywords = 0

        for faq in self.faq_data:
            match_count = 0
            for keyword in faq["keywords"]:
                if keyword.lower() in question_lower:
                    match_count += 1

            if match_count > max_keywords:
                max_keywords = match_count
                best_match = faq

        # 至少匹配1个关键词
        if max_keywords >= 1:
            return best_match

        return None

    def get_response(self, user_id: str, message: str, context: Dict = None) -> str:
        """
        获取客服回复（优先使用FAQ）

        Args:
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息

        Returns:
            str: 回复内容
        """
        # 先尝试匹配FAQ
        faq = self.find_faq(message)

        if faq:
            # 使用FAQ答案
            return faq["answer"]

        # 没有匹配的FAQ，使用大模型
        return super().get_response(user_id, message, context)


class RAGChatbot(Chatbot):
    """基于RAG的智能客服（带知识库检索）"""

    def __init__(self, llm_client=None, knowledge_base=None):
        super().__init__(llm_client)
        self.knowledge_base = knowledge_base or []

    def retrieve_knowledge(self, query: str, top_k: int = 3) -> List[str]:
        """
        检索知识库

        Args:
            query: 查询
            top_k: 返回数量

        Returns:
            list: 相关知识片段
        """
        # 简单的关键词匹配检索
        # 实际项目中应该使用向量数据库（如FAISS、Milvus等）
        query_lower = query.lower()

        scored_knowledge = []
        for knowledge in self.knowledge_base:
            score = 0
            content_lower = knowledge["content"].lower()

            # 计算匹配分数
            for word in query_lower.split():
                if word in content_lower:
                    score += 1

            if score > 0:
                scored_knowledge.append((score, knowledge["content"]))

        # 按分数排序
        scored_knowledge.sort(key=lambda x: x[0], reverse=True)

        return [content for _, content in scored_knowledge[:top_k]]

    def get_response(self, user_id: str, message: str, context: Dict = None) -> str:
        """
        获取客服回复（基于RAG）

        Args:
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息

        Returns:
            str: 回复内容
        """
        # 检索相关知识
        relevant_knowledge = self.retrieve_knowledge(message)

        # 构建增强的系统提示
        system_prompt = self._build_system_prompt(context)

        if relevant_knowledge:
            knowledge_text = "\n\n相关知识库内容：\n"
            for i, knowledge in enumerate(relevant_knowledge, 1):
                knowledge_text += f"{i}. {knowledge}\n"

            system_prompt += knowledge_text
            system_prompt += "\n请结合以上知识库内容回答用户的问题。如果知识库中没有相关信息，请根据你的知识回答。"

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史消息
        history = self.conversation_history.get(user_id, [])
        messages.extend(history[-self.max_history:])

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        # 调用LLM获取回复
        response = self.llm_client.chat_completion(messages)

        if response:
            # 更新对话历史
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            history = self.conversation_history[user_id]
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

            # 限制历史长度
            if len(history) > self.max_history * 2:
                self.conversation_history[user_id] = history[-self.max_history * 2:]

        return response or "抱歉，我暂时无法回答您的问题，请稍后再试。"


if __name__ == "__main__":
    # 测试智能客服
    chatbot = FAQChatbot()

    # 测试FAQ匹配
    response = chatbot.get_response("user1", "如何发布商品？")
    print(f"用户：如何发布商品？")
    print(f"客服：{response}")
    print()

    # 测试大模型回复
    response = chatbot.get_response("user1", "你们平台有什么特色？")
    print(f"用户：你们平台有什么特色？")
    print(f"客服：{response}")
