"""
用户行为采集器
采集用户行为数据并发送到Kafka
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import uuid
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

from config.collector_config import CollectorConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BehaviorCollector:
    """用户行为采集器类"""

    def __init__(self):
        self.config = CollectorConfig
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        """初始化Kafka生产者"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432
            )
            logger.info("Kafka生产者初始化成功")
        except Exception as e:
            logger.error(f"Kafka生产者初始化失败: {str(e)}")
            raise

    def collect_behavior(self, user_id, product_id, behavior_type, behavior_value=None,
                         page_url=None, referer_url=None, user_agent=None, ip_address=None):
        """
        采集用户行为数据

        Args:
            user_id: 用户ID
            product_id: 商品ID
            behavior_type: 行为类型
            behavior_value: 行为值
            page_url: 页面URL
            referer_url: 来源URL
            user_agent: 用户代理
            ip_address: IP地址

        Returns:
            bool: 是否采集成功
        """
        try:
            # 验证行为类型
            if behavior_type not in self.config.BEHAVIOR_TYPES:
                logger.warning(f"无效的行为类型: {behavior_type}")
                return False

            # 构建行为数据
            behavior_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "product_id": product_id,
                "behavior_type": behavior_type,
                "behavior_value": behavior_value,
                "behavior_weight": self.config.BEHAVIOR_WEIGHTS.get(behavior_type, 1),
                "page_url": page_url,
                "referer_url": referer_url,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": int(time.time() * 1000)
            }

            # 发送到Kafka
            key = f"{user_id}_{product_id}" if user_id else None
            future = self.producer.send(
                self.config.KAFKA_TOPIC_BEHAVIOR,
                value=behavior_data,
                key=key
            )

            # 异步回调
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)

            logger.debug(f"行为数据采集成功: {behavior_type}, user_id={user_id}, product_id={product_id}")
            return True

        except Exception as e:
            logger.error(f"行为数据采集失败: {str(e)}")
            return False

    def _on_send_success(self, record_metadata):
        """发送成功回调"""
        logger.debug(f"消息发送成功: topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")

    def _on_send_error(self, exception):
        """发送失败回调"""
        logger.error(f"消息发送失败: {str(exception)}")

    def batch_collect(self, behavior_list):
        """
        批量采集行为数据

        Args:
            behavior_list: 行为数据列表

        Returns:
            int: 成功采集的数量
        """
        success_count = 0
        for behavior in behavior_list:
            if self.collect_behavior(**behavior):
                success_count += 1

        logger.info(f"批量行为数据采集完成，成功 {success_count}/{len(behavior_list)}")
        return success_count

    def collect_view(self, user_id, product_id, **kwargs):
        """采集浏览行为"""
        return self.collect_behavior(user_id, product_id, "view", **kwargs)

    def collect_click(self, user_id, product_id, **kwargs):
        """采集点击行为"""
        return self.collect_behavior(user_id, product_id, "click", **kwargs)

    def collect_favorite(self, user_id, product_id, **kwargs):
        """采集收藏行为"""
        return self.collect_behavior(user_id, product_id, "favorite", **kwargs)

    def collect_cart(self, user_id, product_id, **kwargs):
        """采集购物车行为"""
        return self.collect_behavior(user_id, product_id, "cart", **kwargs)

    def collect_buy(self, user_id, product_id, **kwargs):
        """采集购买行为"""
        return self.collect_behavior(user_id, product_id, "buy", **kwargs)

    def close(self):
        """关闭生产者"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka生产者已关闭")


class BehaviorConsumer:
    """用户行为消费者类"""

    def __init__(self):
        self.config = CollectorConfig
        self.consumer = None
        self._init_consumer()

    def _init_consumer(self):
        """初始化Kafka消费者"""
        try:
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                self.config.KAFKA_TOPIC_BEHAVIOR,
                bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.config.KAFKA_GROUP_ID,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            logger.info("Kafka消费者初始化成功")
        except Exception as e:
            logger.error(f"Kafka消费者初始化失败: {str(e)}")
            raise

    def consume(self, handler_func):
        """
        消费行为数据

        Args:
            handler_func: 处理函数
        """
        logger.info("开始消费行为数据...")
        try:
            for message in self.consumer:
                try:
                    behavior_data = message.value
                    handler_func(behavior_data)
                except Exception as e:
                    logger.error(f"处理行为数据失败: {str(e)}")
        except KeyboardInterrupt:
            logger.info("消费者被中断")
        finally:
            self.close()

    def close(self):
        """关闭消费者"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka消费者已关闭")


if __name__ == "__main__":
    # 测试采集器
    collector = BehaviorCollector()

    # 测试采集浏览行为
    collector.collect_view(
        user_id=1,
        product_id=100,
        page_url="/product/100",
        referer_url="/",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1"
    )

    collector.close()
