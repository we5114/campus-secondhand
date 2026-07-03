"""
ETL任务
数据抽取、转换、加载
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_date, datediff, when, lit, concat_ws
from pyspark.sql.types import IntegerType, FloatType
import logging

from utils.spark_utils import create_spark_session, read_mysql_table, write_hive_table
from config.spark_config import SparkConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLJob:
    """ETL任务类"""

    def __init__(self, spark=None):
        self.spark = spark or create_spark_session("ETLJob")

    def extract_user_data(self):
        """
        抽取用户数据到ODS层

        Returns:
            DataFrame: 用户数据
        """
        logger.info("抽取用户数据...")

        # 从MySQL读取用户表
        user_df = read_mysql_table(self.spark, "user")

        # 写入ODS层
        user_df.write.mode("overwrite").saveAsTable("campus_secondhand.ods_user_info")

        logger.info(f"用户数据抽取完成，共 {user_df.count()} 条记录")
        return user_df

    def extract_product_data(self):
        """
        抽取商品数据到ODS层

        Returns:
            DataFrame: 商品数据
        """
        logger.info("抽取商品数据...")

        # 从MySQL读取商品表
        product_df = read_mysql_table(self.spark, "product")

        # 写入ODS层
        product_df.write.mode("overwrite").saveAsTable("campus_secondhand.ods_product_info")

        logger.info(f"商品数据抽取完成，共 {product_df.count()} 条记录")
        return product_df

    def extract_order_data(self):
        """
        抽取订单数据到ODS层

        Returns:
            DataFrame: 订单数据
        """
        logger.info("抽取订单数据...")

        # 从MySQL读取订单表
        order_df = read_mysql_table(self.spark, "order_info")

        # 写入ODS层
        order_df.write.mode("overwrite").saveAsTable("campus_secondhand.ods_order_info")

        logger.info(f"订单数据抽取完成，共 {order_df.count()} 条记录")
        return order_df

    def extract_behavior_data(self):
        """
        抽取用户行为数据到ODS层

        Returns:
            DataFrame: 用户行为数据
        """
        logger.info("抽取用户行为数据...")

        # 从MySQL读取用户行为表
        behavior_df = read_mysql_table(self.spark, "user_behavior")

        # 写入ODS层
        behavior_df.write.mode("overwrite").saveAsTable("campus_secondhand.ods_user_behavior_log")

        logger.info(f"用户行为数据抽取完成，共 {behavior_df.count()} 条记录")
        return behavior_df

    def transform_user_detail(self):
        """
        转换用户明细宽表到DWD层
        """
        logger.info("转换用户明细宽表...")

        # 从ODS层读取用户数据
        user_df = self.spark.table("campus_secondhand.ods_user_info")

        # 数据清洗和转换
        user_detail_df = user_df.select(
            col("id").alias("user_id"),
            col("username"),
            col("nickname"),
            col("phone"),
            col("email"),
            col("avatar"),
            col("gender"),
            col("grade"),
            col("major"),
            col("campus"),
            col("status"),
            col("user_level"),
            col("is_real_name"),
            col("last_login_time"),
            col("last_login_ip"),
            col("create_time"),
            col("update_time"),
            current_date().alias("dt")
        )

        # 写入DWD层
        user_detail_df.write.mode("overwrite").partitionBy("dt") \
            .saveAsTable("campus_secondhand.dwd_user_detail")

        logger.info(f"用户明细宽表转换完成，共 {user_detail_df.count()} 条记录")

    def transform_product_detail(self):
        """
        转换商品明细宽表到DWD层
        """
        logger.info("转换商品明细宽表...")

        # 从ODS层读取商品数据
        product_df = self.spark.table("campus_secondhand.ods_product_info")

        # 数据清洗和转换
        product_detail_df = product_df.select(
            col("id").alias("product_id"),
            col("seller_id"),
            col("category_id"),
            col("title"),
            col("description"),
            col("price"),
            col("original_price"),
            col("condition"),
            col("quality"),
            col("trade_type"),
            col("location"),
            col("status"),
            col("view_count"),
            col("favorite_count"),
            col("chat_count"),
            col("is_top"),
            col("is_recommend"),
            col("audit_status"),
            col("create_time"),
            col("update_time"),
            # 计算商品上架天数
            datediff(current_date(), col("create_time")).alias("days_on_shelf"),
            # 计算折扣率
            when(col("original_price") > 0,
                 (col("price") / col("original_price")).cast(FloatType())
                 ).otherwise(lit(1.0)).alias("discount_rate"),
            current_date().alias("dt")
        )

        # 写入DWD层
        product_detail_df.write.mode("overwrite").partitionBy("dt") \
            .saveAsTable("campus_secondhand.dwd_product_detail")

        logger.info(f"商品明细宽表转换完成，共 {product_detail_df.count()} 条记录")

    def transform_order_detail(self):
        """
        转换订单明细宽表到DWD层
        """
        logger.info("转换订单明细宽表...")

        # 从ODS层读取订单数据
        order_df = self.spark.table("campus_secondhand.ods_order_info")

        # 数据清洗和转换
        order_detail_df = order_df.select(
            col("id").alias("order_id"),
            col("order_no"),
            col("buyer_id"),
            col("seller_id"),
            col("product_id"),
            col("product_title"),
            col("product_image"),
            col("product_price"),
            col("quantity"),
            col("total_amount"),
            col("pay_amount"),
            col("freight_amount"),
            col("discount_amount"),
            col("pay_type"),
            col("trade_type"),
            col("status"),
            col("receiver_name"),
            col("receiver_phone"),
            col("receiver_address"),
            col("pay_time"),
            col("ship_time"),
            col("finish_time"),
            col("cancel_time"),
            col("cancel_reason"),
            col("remark"),
            col("create_time"),
            col("update_time"),
            # 计算订单时长（分钟）
            when(col("finish_time").isNotNull(),
                 (col("finish_time").cast("long") - col("create_time").cast("long")) / 60
                 ).otherwise(lit(None)).alias("order_duration_minutes"),
            current_date().alias("dt")
        )

        # 写入DWD层
        order_detail_df.write.mode("overwrite").partitionBy("dt") \
            .saveAsTable("campus_secondhand.dwd_order_detail")

        logger.info(f"订单明细宽表转换完成，共 {order_detail_df.count()} 条记录")

    def transform_behavior_detail(self):
        """
        转换用户行为明细到DWD层
        """
        logger.info("转换用户行为明细...")

        # 从ODS层读取行为数据
        behavior_df = self.spark.table("campus_secondhand.ods_user_behavior_log")

        # 定义行为权重
        behavior_weights = {
            "view": 1,
            "click": 2,
            "favorite": 5,
            "cart": 8,
            "buy": 10
        }

        # 数据清洗和转换
        behavior_detail_df = behavior_df.select(
            col("id").alias("behavior_id"),
            col("user_id"),
            col("product_id"),
            col("behavior_type"),
            # 添加行为权重
            when(col("behavior_type") == "view", lit(1))
            .when(col("behavior_type") == "click", lit(2))
            .when(col("behavior_type") == "favorite", lit(5))
            .when(col("behavior_type") == "cart", lit(8))
            .when(col("behavior_type") == "buy", lit(10))
            .otherwise(lit(1)).alias("behavior_weight"),
            col("behavior_value"),
            col("page_url"),
            col("referer_url"),
            col("user_agent"),
            col("ip_address"),
            col("create_time"),
            current_date().alias("dt")
        )

        # 写入DWD层
        behavior_detail_df.write.mode("overwrite").partitionBy("dt") \
            .saveAsTable("campus_secondhand.dwd_user_behavior_detail")

        logger.info(f"用户行为明细转换完成，共 {behavior_detail_df.count()} 条记录")

    def aggregate_user_stat(self):
        """
        聚合用户日统计到DWS层
        """
        logger.info("聚合用户日统计...")

        # 从DWD层读取数据
        self.spark.sql("""
            INSERT OVERWRITE TABLE campus_secondhand.dws_user_stat_daily
            PARTITION(dt)
            SELECT
                user_id,
                count(*) as behavior_count,
                count(distinct product_id) as product_count,
                sum(behavior_weight) as total_score,
                dt
            FROM campus_secondhand.dwd_user_behavior_detail
            GROUP BY user_id, dt
        """)

        logger.info("用户日统计聚合完成")

    def aggregate_product_stat(self):
        """
        聚合商品日统计到DWS层
        """
        logger.info("聚合商品日统计...")

        # 从DWD层读取数据
        self.spark.sql("""
            INSERT OVERWRITE TABLE campus_secondhand.dws_product_stat_daily
            PARTITION(dt)
            SELECT
                product_id,
                count(*) as behavior_count,
                count(distinct user_id) as user_count,
                sum(behavior_weight) as total_score,
                dt
            FROM campus_secondhand.dwd_user_behavior_detail
            GROUP BY product_id, dt
        """)

        logger.info("商品日统计聚合完成")

    def aggregate_trade_stat(self):
        """
        聚合交易日统计到DWS层
        """
        logger.info("聚合交易日统计...")

        # 从DWD层读取数据
        self.spark.sql("""
            INSERT OVERWRITE TABLE campus_secondhand.dws_trade_stat_daily
            PARTITION(dt)
            SELECT
                count(*) as order_count,
                count(distinct buyer_id) as buyer_count,
                count(distinct seller_id) as seller_count,
                sum(pay_amount) as total_amount,
                avg(pay_amount) as avg_amount,
                dt
            FROM campus_secondhand.dwd_order_detail
            WHERE status = 3  -- 已完成
            GROUP BY dt
        """)

        logger.info("交易日统计聚合完成")

    def run(self):
        """运行ETL任务"""
        logger.info("开始执行ETL任务...")

        try:
            # 1. 数据抽取（ODS层）
            self.extract_user_data()
            self.extract_product_data()
            self.extract_order_data()
            self.extract_behavior_data()

            # 2. 数据转换（DWD层）
            self.transform_user_detail()
            self.transform_product_detail()
            self.transform_order_detail()
            self.transform_behavior_detail()

            # 3. 数据聚合（DWS层）
            self.aggregate_user_stat()
            self.aggregate_product_stat()
            self.aggregate_trade_stat()

            logger.info("ETL任务执行完成")

        except Exception as e:
            logger.error(f"ETL任务执行失败: {str(e)}")
            raise


if __name__ == "__main__":
    job = ETLJob()
    job.run()
