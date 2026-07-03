"""
推荐计算任务
基于用户行为数据计算推荐结果
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, desc, row_number, collect_list, struct
from pyspark.sql.window import Window
import logging

from utils.spark_utils import create_spark_session, get_redis_client, save_recommend_to_redis
from config.spark_config import SparkConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendJob:
    """推荐计算任务类"""

    def __init__(self, spark=None):
        self.spark = spark or create_spark_session("RecommendJob")
        self.redis_client = get_redis_client()
        self.config = SparkConfig.RECOMMEND_CONFIG

    def load_user_behavior(self):
        """
        加载用户行为数据

        Returns:
            DataFrame: 用户行为数据
        """
        logger.info("加载用户行为数据...")

        # 从Hive读取用户行为数据
        behavior_df = self.spark.sql("""
            SELECT
                user_id,
                product_id,
                behavior_type,
                behavior_weight,
                create_time
            FROM campus_secondhand.dwd_user_behavior_detail
            WHERE dt >= date_sub(current_date(), 30)
        """)

        logger.info(f"用户行为数据加载完成，共 {behavior_df.count()} 条记录")
        return behavior_df

    def calculate_user_product_score(self, behavior_df):
        """
        计算用户-商品评分矩阵

        Args:
            behavior_df: 用户行为数据

        Returns:
            DataFrame: 用户-商品评分
        """
        logger.info("计算用户-商品评分矩阵...")

        # 按用户和商品聚合，计算总评分
        score_df = behavior_df.groupBy("user_id", "product_id") \
            .agg(
                spark_sum("behavior_weight").alias("score"),
                count("*").alias("behavior_count")
            ) \
            .filter(col("score") > 0)

        logger.info(f"用户-商品评分计算完成，共 {score_df.count()} 条记录")
        return score_df

    def calculate_hot_products(self, behavior_df):
        """
        计算热门商品

        Args:
            behavior_df: 用户行为数据

        Returns:
            list: 热门商品列表
        """
        logger.info("计算热门商品...")

        # 按商品聚合，计算热度
        hot_df = behavior_df.groupBy("product_id") \
            .agg(
                spark_sum("behavior_weight").alias("hot_score"),
                count("*").alias("behavior_count"),
                count("user_id").alias("user_count")
            ) \
            .orderBy(desc("hot_score")) \
            .limit(self.config["hot_recommend_count"])

        hot_products = [row.product_id for row in hot_df.collect()]

        logger.info(f"热门商品计算完成，共 {len(hot_products)} 个")
        return hot_products

    def calculate_new_products(self):
        """
        计算新品推荐

        Returns:
            list: 新品列表
        """
        logger.info("计算新品推荐...")

        # 从Hive读取最新上架的商品
        new_df = self.spark.sql("""
            SELECT
                id as product_id
            FROM campus_secondhand.dwd_product_detail
            WHERE status = 1
              AND dt >= date_sub(current_date(), 7)
            ORDER BY create_time DESC
            LIMIT {}
        """.format(self.config["new_recommend_count"]))

        new_products = [row.product_id for row in new_df.collect()]

        logger.info(f"新品推荐计算完成，共 {len(new_products)} 个")
        return new_products

    def calculate_user_cf(self, score_df):
        """
        基于用户的协同过滤推荐

        Args:
            score_df: 用户-商品评分

        Returns:
            dict: 用户推荐结果 {user_id: [product_id, ...]}
        """
        logger.info("计算UserCF推荐...")

        # 构建用户-商品评分矩阵
        user_products = score_df.groupBy("user_id") \
            .agg(collect_list(struct("product_id", "score")).alias("products"))

        # 简化实现：基于共同评分商品计算用户相似度
        # 实际项目中应该使用更高效的算法（如LSH、ALS等）

        user_recommendations = {}

        # 收集所有用户
        users = score_df.select("user_id").distinct().collect()
        user_ids = [row.user_id for row in users]

        # 为每个用户计算推荐
        for user_id in user_ids[:100]:  # 限制计算量，实际项目中应该分布式计算
            # 获取用户已评分的商品
            user_rated = score_df.filter(col("user_id") == user_id) \
                .select("product_id", "score") \
                .collect()

            user_rated_dict = {row.product_id: row.score for row in user_rated}

            if not user_rated_dict:
                continue

            # 计算相似用户（简化：找有共同评分商品的用户）
            similar_users = score_df.filter(
                col("product_id").isin(list(user_rated_dict.keys()))
            ).groupBy("user_id") \
                .agg(count("*").alias("common_count")) \
                .filter(col("user_id") != user_id) \
                .orderBy(desc("common_count")) \
                .limit(self.config["user_cf_neighbors"]) \
                .collect()

            # 基于相似用户的评分计算推荐
            product_scores = {}
            product_support = {}

            for sim_user in similar_users:
                sim_user_id = sim_user.user_id

                # 获取相似用户的评分
                sim_user_rated = score_df.filter(col("user_id") == sim_user_id) \
                    .select("product_id", "score") \
                    .collect()

                for row in sim_user_rated:
                    pid = row.product_id
                    score = row.score

                    if pid not in user_rated_dict:  # 排除用户已评分的商品
                        product_scores[pid] = product_scores.get(pid, 0) + score
                        product_support[pid] = product_support.get(pid, 0) + 1

            # 排序并取TopN
            sorted_products = sorted(
                product_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:self.config["recommend_count"]]

            user_recommendations[user_id] = [pid for pid, _ in sorted_products]

        logger.info(f"UserCF推荐计算完成，共 {len(user_recommendations)} 个用户")
        return user_recommendations

    def calculate_item_cf(self, score_df):
        """
        基于物品的协同过滤推荐

        Args:
            score_df: 用户-商品评分

        Returns:
            dict: 商品相似矩阵 {product_id: [similar_product_id, ...]}
        """
        logger.info("计算ItemCF推荐...")

        # 构建商品-用户评分矩阵
        product_users = score_df.groupBy("product_id") \
            .agg(collect_list(struct("user_id", "score")).alias("users"))

        # 简化实现：计算商品相似度
        # 实际项目中应该使用更高效的算法

        product_similarities = {}

        # 收集所有商品
        products = score_df.select("product_id").distinct().collect()
        product_ids = [row.product_id for row in products]

        # 为每个商品计算相似商品
        for product_id in product_ids[:100]:  # 限制计算量
            # 获取评分过该商品的用户
            product_rated_users = score_df.filter(col("product_id") == product_id) \
                .select("user_id", "score") \
                .collect()

            product_rated_dict = {row.user_id: row.score for row in product_rated_users}

            if not product_rated_dict:
                continue

            # 计算相似商品（简化：找有共同评分用户的商品）
            similar_products = score_df.filter(
                col("user_id").isin(list(product_rated_dict.keys()))
            ).groupBy("product_id") \
                .agg(count("*").alias("common_count")) \
                .filter(col("product_id") != product_id) \
                .orderBy(desc("common_count")) \
                .limit(self.config["item_cf_neighbors"]) \
                .collect()

            product_similarities[product_id] = [row.product_id for row in similar_products]

        logger.info(f"ItemCF推荐计算完成，共 {len(product_similarities)} 个商品")
        return product_similarities

    def save_recommendations(self, user_recommendations, hot_products, new_products):
        """
        保存推荐结果

        Args:
            user_recommendations: 用户推荐结果
            hot_products: 热门商品
            new_products: 新品
        """
        logger.info("保存推荐结果...")

        # 保存热门推荐
        save_recommend_to_redis(
            self.redis_client,
            "recommend:hot",
            hot_products,
            expire=3600  # 1小时过期
        )

        # 保存新品推荐
        save_recommend_to_redis(
            self.redis_client,
            "recommend:new",
            new_products,
            expire=3600
        )

        # 保存用户个性化推荐
        for user_id, products in user_recommendations.items():
            save_recommend_to_redis(
                self.redis_client,
                f"recommend:user:{user_id}",
                products,
                expire=86400  # 24小时过期
            )

        logger.info("推荐结果保存完成")

    def run(self):
        """运行推荐计算任务"""
        logger.info("开始执行推荐计算任务...")

        try:
            # 1. 加载用户行为数据
            behavior_df = self.load_user_behavior()

            # 2. 计算用户-商品评分
            score_df = self.calculate_user_product_score(behavior_df)

            # 3. 计算热门商品
            hot_products = self.calculate_hot_products(behavior_df)

            # 4. 计算新品推荐
            new_products = self.calculate_new_products()

            # 5. 计算UserCF推荐
            user_recommendations = self.calculate_user_cf(score_df)

            # 6. 计算ItemCF推荐
            product_similarities = self.calculate_item_cf(score_df)

            # 7. 保存推荐结果
            self.save_recommendations(user_recommendations, hot_products, new_products)

            logger.info("推荐计算任务执行完成")

        except Exception as e:
            logger.error(f"推荐计算任务执行失败: {str(e)}")
            raise


if __name__ == "__main__":
    job = RecommendJob()
    job.run()
