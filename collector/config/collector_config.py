"""
数据采集配置
"""
import os


class CollectorConfig:
    """数据采集配置类"""

    # Kafka配置
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_BEHAVIOR = os.environ.get("KAFKA_TOPIC_BEHAVIOR", "user_behavior")
    KAFKA_TOPIC_PRODUCT = os.environ.get("KAFKA_TOPIC_PRODUCT", "product_event")
    KAFKA_TOPIC_ORDER = os.environ.get("KAFKA_TOPIC_ORDER", "order_event")
    KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "campus-secondhand-collector")

    # MySQL配置
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "campus_secondhand")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")

    # Hive配置
    HIVE_METASTORE_URIS = os.environ.get("HIVE_METASTORE_URIS", "thrift://localhost:9083")
    HIVE_WAREHOUSE_DIR = os.environ.get("HIVE_WAREHOUSE_DIR", "/user/hive/warehouse")

    # Redis配置
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))

    # 数据采集配置
    BEHAVIOR_TYPES = ["view", "click", "favorite", "cart", "buy"]
    BEHAVIOR_WEIGHTS = {
        "view": 1,
        "click": 2,
        "favorite": 5,
        "cart": 8,
        "buy": 10
    }

    # 数据同步配置
    SYNC_BATCH_SIZE = int(os.environ.get("SYNC_BATCH_SIZE", 1000))
    SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", 60))  # 秒

    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "/var/log/campus-secondhand/collector.log")

    @classmethod
    def get_mysql_url(cls):
        """获取MySQL连接URL"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}?charset=utf8mb4"
