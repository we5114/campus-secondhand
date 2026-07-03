"""
Spark工具类
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, current_date, datediff
from pyspark.sql.types import FloatType, IntegerType, StringType
import redis
import logging

from config.spark_config import SparkConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session(app_name=None, enable_hive=True):
    """
    创建SparkSession

    Args:
        app_name: 应用名称
        enable_hive: 是否启用Hive支持

    Returns:
        SparkSession
    """
    builder = SparkSession.builder \
        .appName(app_name or SparkConfig.APP_NAME) \
        .master(SparkConfig.MASTER) \
        .config("spark.sql.warehouse.dir", SparkConfig.HIVE_WAREHOUSE_DIR) \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.kryoserializer.buffer.max", "1024m") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.adaptive.skewJoin.enabled", "true")

    if enable_hive:
        builder = builder.enableHiveSupport()

    spark = builder.getOrCreate()

    logger.info(f"SparkSession创建成功: {app_name or SparkConfig.APP_NAME}")
    return spark


def get_redis_client():
    """
    获取Redis客户端

    Returns:
        Redis客户端
    """
    return redis.Redis(
        host=SparkConfig.REDIS_HOST,
        port=SparkConfig.REDIS_PORT,
        db=SparkConfig.REDIS_DB,
        decode_responses=True
    )


def read_mysql_table(spark, table_name):
    """
    从MySQL读取表数据

    Args:
        spark: SparkSession
        table_name: 表名

    Returns:
        DataFrame
    """
    df = spark.read.jdbc(
        url=SparkConfig.get_mysql_url(),
        table=table_name,
        properties=SparkConfig.get_mysql_properties()
    )
    logger.info(f"从MySQL读取表 {table_name}, 数据量: {df.count()}")
    return df


def write_mysql_table(df, table_name, mode="append"):
    """
    写入数据到MySQL

    Args:
        df: DataFrame
        table_name: 表名
        mode: 写入模式
    """
    df.write.jdbc(
        url=SparkConfig.get_mysql_url(),
        table=table_name,
        mode=mode,
        properties=SparkConfig.get_mysql_properties()
    )
    logger.info(f"写入数据到MySQL表 {table_name}, 模式: {mode}")


def read_hive_table(spark, table_name, database="campus_secondhand"):
    """
    从Hive读取表数据

    Args:
        spark: SparkSession
        table_name: 表名
        database: 数据库名

    Returns:
        DataFrame
    """
    full_table = f"{database}.{table_name}"
    df = spark.table(full_table)
    logger.info(f"从Hive读取表 {full_table}, 数据量: {df.count()}")
    return df


def write_hive_table(df, table_name, database="campus_secondhand", mode="overwrite"):
    """
    写入数据到Hive

    Args:
        df: DataFrame
        table_name: 表名
        database: 数据库名
        mode: 写入模式
    """
    full_table = f"{database}.{table_name}"
    df.write.mode(mode).saveAsTable(full_table)
    logger.info(f"写入数据到Hive表 {full_table}, 模式: {mode}")


def calculate_cosine_similarity(vec1, vec2):
    """
    计算余弦相似度

    Args:
        vec1: 向量1
        vec2: 向量2

    Returns:
        相似度
    """
    import math

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def calculate_jaccard_similarity(set1, set2):
    """
    计算Jaccard相似度

    Args:
        set1: 集合1
        set2: 集合2

    Returns:
        相似度
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 0.0

    return intersection / union


def save_recommend_to_redis(redis_client, key, recommend_list, expire=86400):
    """
    保存推荐结果到Redis

    Args:
        redis_client: Redis客户端
        key: Redis键
        recommend_list: 推荐列表
        expire: 过期时间（秒）
    """
    import json

    redis_client.setex(
        key,
        expire,
        json.dumps(recommend_list)
    )
    logger.info(f"保存推荐结果到Redis: {key}, 数量: {len(recommend_list)}")


def get_recommend_from_redis(redis_client, key):
    """
    从Redis获取推荐结果

    Args:
        redis_client: Redis客户端
        key: Redis键

    Returns:
        推荐列表
    """
    import json

    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def udf_calculate_days_between(date_col):
    """
    UDF: 计算日期差（天）

    Args:
        date_col: 日期列

    Returns:
        天数
    """
    return datediff(current_date(), date_col)


def udf_normalize_score(score, min_score, max_score):
    """
    UDF: 归一化分数到0-1

    Args:
        score: 原始分数
        min_score: 最小分数
        max_score: 最大分数

    Returns:
        归一化后的分数
    """
    if max_score == min_score:
        return 0.5
    return (score - min_score) / (max_score - min_score)


# 注册UDF
def register_udfs(spark):
    """
    注册自定义UDF

    Args:
        spark: SparkSession
    """
    spark.udf.register("cosine_similarity", calculate_cosine_similarity, FloatType())
    spark.udf.register("jaccard_similarity", calculate_jaccard_similarity, FloatType())
    logger.info("UDF注册完成")
