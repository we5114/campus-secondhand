"""
用户画像计算任务
基于用户行为数据构建用户画像
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, desc, collect_list, struct, when, lit, size
from pyspark.sql.types import IntegerType, FloatType, ArrayType, StringType
import logging

from utils.spark_utils import create_spark_session, write_hive_table
from config.spark_config import SparkConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserProfileJob:
    """用户画像计算任务类"""

    def __init__(self, spark=None):
        self.spark = spark or create_spark_session("UserProfileJob")

    def calculate_user_behavior_tags(self):
        """
        计算用户行为标签

        Returns:
            DataFrame: 用户行为标签
        """
        logger.info("计算用户行为标签...")

        # 从DWD层读取用户行为数据
        behavior_df = self.spark.sql("""
            SELECT
                user_id,
                product_id,
                behavior_type,
                behavior_weight,
                category_id,
                dt
            FROM campus_secondhand.dwd_user_behavior_detail
            WHERE dt >= date_sub(current_date(), 30)
        """)

        # 计算用户行为统计
        user_behavior_stat = behavior_df.groupBy("user_id").agg(
            count("*").alias("total_behavior_count"),
            spark_sum("behavior_weight").alias("total_behavior_score"),
            count("product_id").alias("view_product_count"),
            count(when(col("behavior_type") == "buy", 1)).alias("buy_count"),
            count(when(col("behavior_type") == "favorite", 1)).alias("favorite_count"),
            count(when(col("behavior_type") == "cart", 1)).alias("cart_count")
        )

        logger.info(f"用户行为标签计算完成，共 {user_behavior_stat.count()} 个用户")
        return user_behavior_stat

    def calculate_user_category_preference(self):
        """
        计算用户品类偏好

        Returns:
            DataFrame: 用户品类偏好
        """
        logger.info("计算用户品类偏好...")

        # 从DWD层读取用户行为数据，关联商品分类
        category_behavior_df = self.spark.sql("""
            SELECT
                b.user_id,
                p.category_id,
                p.category_name,
                sum(b.behavior_weight) as category_score
            FROM campus_secondhand.dwd_user_behavior_detail b
            LEFT JOIN campus_secondhand.dwd_product_detail p
                ON b.product_id = p.product_id
            WHERE b.dt >= date_sub(current_date(), 30)
              AND p.category_id IS NOT NULL
            GROUP BY b.user_id, p.category_id, p.category_name
        """)

        # 计算每个用户的TopN品类偏好
        window_spec = Window.partitionBy("user_id").orderBy(desc("category_score"))

        user_category_pref = category_behavior_df.withColumn(
            "rank",
            row_number().over(window_spec)
        ).filter(col("rank") <= 5)

        # 聚合为列表
        user_category_list = user_category_pref.groupBy("user_id").agg(
            collect_list(struct(
                col("category_id"),
                col("category_name"),
                col("category_score")
            )).alias("category_preferences")
        )

        logger.info(f"用户品类偏好计算完成，共 {user_category_list.count()} 个用户")
        return user_category_list

    def calculate_user_price_preference(self):
        """
        计算用户价格偏好

        Returns:
            DataFrame: 用户价格偏好
        """
        logger.info("计算用户价格偏好...")

        # 从DWD层读取用户行为数据，关联商品价格
        price_behavior_df = self.spark.sql("""
            SELECT
                b.user_id,
                p.price,
                b.behavior_weight
            FROM campus_secondhand.dwd_user_behavior_detail b
            LEFT JOIN campus_secondhand.dwd_product_detail p
                ON b.product_id = p.product_id
            WHERE b.dt >= date_sub(current_date(), 30)
              AND p.price IS NOT NULL
              AND b.behavior_type IN ('buy', 'cart', 'favorite')
        """)

        # 计算用户价格区间偏好
        user_price_pref = price_behavior_df.groupBy("user_id").agg(
            spark_sum(when(col("price") < 50, col("behavior_weight"))).alias("price_0_50"),
            spark_sum(when((col("price") >= 50) & (col("price") < 100), col("behavior_weight"))).alias("price_50_100"),
            spark_sum(when((col("price") >= 100) & (col("price") < 300), col("behavior_weight"))).alias("price_100_300"),
            spark_sum(when((col("price") >= 300) & (col("price") < 500), col("behavior_weight"))).alias("price_300_500"),
            spark_sum(when(col("price") >= 500, col("behavior_weight"))).alias("price_500_plus"),
            avg("price").alias("avg_price"),
            percentile_approx("price", 0.5).alias("median_price")
        )

        logger.info(f"用户价格偏好计算完成，共 {user_price_pref.count()} 个用户")
        return user_price_pref

    def calculate_user_activity_level(self):
        """
        计算用户活跃度等级

        Returns:
            DataFrame: 用户活跃度
        """
        logger.info("计算用户活跃度等级...")

        # 从DWD层读取用户行为数据
        activity_df = self.spark.sql("""
            SELECT
                user_id,
                count(distinct dt) as active_days,
                count(*) as total_behavior,
                sum(behavior_weight) as total_score
            FROM campus_secondhand.dwd_user_behavior_detail
            WHERE dt >= date_sub(current_date(), 30)
            GROUP BY user_id
        """)

        # 计算活跃度等级
        user_activity = activity_df.withColumn(
            "activity_level",
            when(col("active_days") >= 20, lit("high"))
            .when(col("active_days") >= 10, lit("medium"))
            .when(col("active_days") >= 3, lit("low"))
            .otherwise(lit("inactive"))
        )

        logger.info(f"用户活跃度等级计算完成，共 {user_activity.count()} 个用户")
        return user_activity

    def build_user_profile(self):
        """
        构建用户画像宽表

        Returns:
            DataFrame: 用户画像宽表
        """
        logger.info("构建用户画像宽表...")

        # 1. 获取用户基本信息
        user_base_df = self.spark.sql("""
            SELECT
                user_id,
                username,
                nickname,
                gender,
                grade,
                major,
                campus,
                user_level,
                is_real_name,
                create_time as register_time
            FROM campus_secondhand.dwd_user_detail
            WHERE dt = current_date()
        """)

        # 2. 计算用户行为标签
        behavior_tags_df = self.calculate_user_behavior_tags()

        # 3. 计算用户品类偏好
        category_pref_df = self.calculate_user_category_preference()

        # 4. 计算用户价格偏好
        price_pref_df = self.calculate_user_price_preference()

        # 5. 计算用户活跃度
        activity_df = self.calculate_user_activity_level()

        # 6. 关联所有数据，构建用户画像宽表
        user_profile_df = user_base_df \
            .join(behavior_tags_df, "user_id", "left") \
            .join(category_pref_df, "user_id", "left") \
            .join(price_pref_df, "user_id", "left") \
            .join(activity_df, "user_id", "left") \
            .withColumn("dt", current_date())

        # 写入ADS层
        user_profile_df.write.mode("overwrite").partitionBy("dt") \
            .saveAsTable("campus_secondhand.ads_user_profile")

        logger.info(f"用户画像宽表构建完成，共 {user_profile_df.count()} 条记录")
        return user_profile_df

    def run(self):
        """运行用户画像计算任务"""
        logger.info("开始执行用户画像计算任务...")

        try:
            # 构建用户画像
            self.build_user_profile()

            logger.info("用户画像计算任务执行完成")

        except Exception as e:
            logger.error(f"用户画像计算任务执行失败: {str(e)}")
            raise


if __name__ == "__main__":
    job = UserProfileJob()
    job.run()
