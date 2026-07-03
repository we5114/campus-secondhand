"""
协同过滤推荐算法
实现基于用户和基于物品的协同过滤
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from collections import defaultdict
import logging

from utils.model_utils import calculate_cosine_similarity, calculate_pearson_correlation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserCF:
    """基于用户的协同过滤"""

    def __init__(self, n_neighbors=50, top_n=100):
        """
        初始化UserCF

        Args:
            n_neighbors: 邻居数量
            top_n: 推荐数量
        """
        self.n_neighbors = n_neighbors
        self.top_n = top_n
        self.user_similarity = None
        self.user_items = None
        self.user_ratings = None

    def fit(self, user_item_matrix):
        """
        训练模型

        Args:
            user_item_matrix: 用户-物品评分矩阵，DataFrame格式，index为用户ID，columns为物品ID
        """
        logger.info("开始训练UserCF模型...")

        self.user_ratings = user_item_matrix
        self.user_items = defaultdict(set)

        # 构建用户-物品字典
        for user_id in user_item_matrix.index:
            items = user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index.tolist()
            self.user_items[user_id] = set(items)

        # 计算用户相似度矩阵
        self.user_similarity = self._calculate_user_similarity(user_item_matrix)

        logger.info(f"UserCF模型训练完成，用户数: {len(user_item_matrix.index)}")

    def _calculate_user_similarity(self, user_item_matrix):
        """
        计算用户相似度矩阵

        Args:
            user_item_matrix: 用户-物品评分矩阵

        Returns:
            dict: 用户相似度字典 {user_id: {similar_user_id: similarity}}
        """
        logger.info("计算用户相似度矩阵...")

        user_similarity = defaultdict(dict)
        user_ids = user_item_matrix.index.tolist()

        # 物品-用户倒排表
        item_users = defaultdict(set)
        for user_id in user_ids:
            items = self.user_items[user_id]
            for item_id in items:
                item_users[item_id].add(user_id)

        # 计算用户共同评分物品数
        user_common_items = defaultdict(lambda: defaultdict(int))
        for item_id, users in item_users.items():
            users_list = list(users)
            for i in range(len(users_list)):
                for j in range(i + 1, len(users_list)):
                    u1 = users_list[i]
                    u2 = users_list[j]
                    user_common_items[u1][u2] += 1
                    user_common_items[u2][u1] += 1

        # 计算相似度
        for u1 in user_ids:
            for u2, common_count in user_common_items[u1].items():
                if u1 != u2:
                    # 使用Jaccard相似度
                    union_count = len(self.user_items[u1] | self.user_items[u2])
                    if union_count > 0:
                        similarity = common_count / union_count
                        user_similarity[u1][u2] = similarity

        logger.info("用户相似度矩阵计算完成")
        return user_similarity

    def recommend(self, user_id):
        """
        为用户推荐物品

        Args:
            user_id: 用户ID

        Returns:
            list: 推荐物品列表 [(item_id, score), ...]
        """
        if user_id not in self.user_similarity:
            logger.warning(f"用户 {user_id} 不在模型中")
            return []

        # 获取用户已评分的物品
        user_rated_items = self.user_items.get(user_id, set())

        # 获取相似用户
        similar_users = sorted(
            self.user_similarity[user_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.n_neighbors]

        # 计算推荐分数
        item_scores = defaultdict(float)
        item_similarity_sum = defaultdict(float)

        for sim_user, similarity in similar_users:
            sim_user_items = self.user_items.get(sim_user, set())

            for item_id in sim_user_items:
                if item_id not in user_rated_items:  # 排除用户已评分的物品
                    rating = self.user_ratings.loc[sim_user, item_id]
                    item_scores[item_id] += similarity * rating
                    item_similarity_sum[item_id] += similarity

        # 归一化分数
        for item_id in item_scores:
            if item_similarity_sum[item_id] > 0:
                item_scores[item_id] /= item_similarity_sum[item_id]

        # 排序并返回TopN
        recommendations = sorted(
            item_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_n]

        return recommendations

    def batch_recommend(self, user_ids):
        """
        批量为用户推荐

        Args:
            user_ids: 用户ID列表

        Returns:
            dict: 用户推荐结果 {user_id: [(item_id, score), ...]}
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.recommend(user_id)
        return results


class ItemCF:
    """基于物品的协同过滤"""

    def __init__(self, n_neighbors=50, top_n=100):
        """
        初始化ItemCF

        Args:
            n_neighbors: 邻居数量
            top_n: 推荐数量
        """
        self.n_neighbors = n_neighbors
        self.top_n = top_n
        self.item_similarity = None
        self.item_users = None
        self.user_ratings = None

    def fit(self, user_item_matrix):
        """
        训练模型

        Args:
            user_item_matrix: 用户-物品评分矩阵
        """
        logger.info("开始训练ItemCF模型...")

        self.user_ratings = user_item_matrix
        self.item_users = defaultdict(set)

        # 构建物品-用户字典
        for user_id in user_item_matrix.index:
            items = user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index.tolist()
            for item_id in items:
                self.item_users[item_id].add(user_id)

        # 计算物品相似度矩阵
        self.item_similarity = self._calculate_item_similarity()

        logger.info(f"ItemCF模型训练完成，物品数: {len(self.item_users)}")

    def _calculate_item_similarity(self):
        """
        计算物品相似度矩阵

        Returns:
            dict: 物品相似度字典 {item_id: {similar_item_id: similarity}}
        """
        logger.info("计算物品相似度矩阵...")

        item_similarity = defaultdict(dict)
        item_ids = list(self.item_users.keys())

        # 计算物品共同评分数
        item_common_users = defaultdict(lambda: defaultdict(int))
        for item_id, users in self.item_users.items():
            users_list = list(users)
            for i in range(len(users_list)):
                for j in range(i + 1, len(users_list)):
                    u1 = users_list[i]
                    u2 = users_list[j]
                    item_common_users[item_id][u2] += 1

        # 计算相似度
        for i1 in item_ids:
            for i2 in item_ids:
                if i1 != i2:
                    # 使用Jaccard相似度
                    common_count = len(self.item_users[i1] & self.item_users[i2])
                    union_count = len(self.item_users[i1] | self.item_users[i2])
                    if union_count > 0:
                        similarity = common_count / union_count
                        item_similarity[i1][i2] = similarity

        logger.info("物品相似度矩阵计算完成")
        return item_similarity

    def recommend(self, user_id):
        """
        为用户推荐物品

        Args:
            user_id: 用户ID

        Returns:
            list: 推荐物品列表 [(item_id, score), ...]
        """
        if user_id not in self.user_ratings.index:
            logger.warning(f"用户 {user_id} 不在模型中")
            return []

        # 获取用户已评分的物品
        user_rated_items = self.user_ratings.loc[user_id]
        user_rated_items = user_rated_items[user_rated_items > 0].to_dict()

        # 计算推荐分数
        item_scores = defaultdict(float)
        item_similarity_sum = defaultdict(float)

        for rated_item, rating in user_rated_items.items():
            # 获取相似物品
            similar_items = sorted(
                self.item_similarity.get(rated_item, {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:self.n_neighbors]

            for sim_item, similarity in similar_items:
                if sim_item not in user_rated_items:  # 排除用户已评分的物品
                    item_scores[sim_item] += similarity * rating
                    item_similarity_sum[sim_item] += similarity

        # 归一化分数
        for item_id in item_scores:
            if item_similarity_sum[item_id] > 0:
                item_scores[item_id] /= item_similarity_sum[item_id]

        # 排序并返回TopN
        recommendations = sorted(
            item_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_n]

        return recommendations

    def get_similar_items(self, item_id, top_n=10):
        """
        获取相似物品

        Args:
            item_id: 物品ID
            top_n: 返回数量

        Returns:
            list: 相似物品列表 [(item_id, similarity), ...]
        """
        if item_id not in self.item_similarity:
            return []

        similar_items = sorted(
            self.item_similarity[item_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return similar_items

    def batch_recommend(self, user_ids):
        """
        批量为用户推荐

        Args:
            user_ids: 用户ID列表

        Returns:
            dict: 用户推荐结果 {user_id: [(item_id, score), ...]}
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.recommend(user_id)
        return results


class HybridCF:
    """混合协同过滤（UserCF + ItemCF）"""

    def __init__(self, user_cf_weight=0.5, item_cf_weight=0.5, top_n=100):
        """
        初始化混合协同过滤

        Args:
            user_cf_weight: UserCF权重
            item_cf_weight: ItemCF权重
            top_n: 推荐数量
        """
        self.user_cf_weight = user_cf_weight
        self.item_cf_weight = item_cf_weight
        self.top_n = top_n
        self.user_cf = None
        self.item_cf = None

    def fit(self, user_item_matrix):
        """
        训练模型

        Args:
            user_item_matrix: 用户-物品评分矩阵
        """
        logger.info("开始训练混合协同过滤模型...")

        # 训练UserCF
        self.user_cf = UserCF(top_n=self.top_n)
        self.user_cf.fit(user_item_matrix)

        # 训练ItemCF
        self.item_cf = ItemCF(top_n=self.top_n)
        self.item_cf.fit(user_item_matrix)

        logger.info("混合协同过滤模型训练完成")

    def recommend(self, user_id):
        """
        为用户推荐物品

        Args:
            user_id: 用户ID

        Returns:
            list: 推荐物品列表 [(item_id, score), ...]
        """
        # 获取UserCF推荐
        user_cf_recs = dict(self.user_cf.recommend(user_id))

        # 获取ItemCF推荐
        item_cf_recs = dict(self.item_cf.recommend(user_id))

        # 混合推荐
        hybrid_scores = defaultdict(float)

        all_items = set(user_cf_recs.keys()) | set(item_cf_recs.keys())

        for item_id in all_items:
            score = (
                self.user_cf_weight * user_cf_recs.get(item_id, 0) +
                self.item_cf_weight * item_cf_recs.get(item_id, 0)
            )
            hybrid_scores[item_id] = score

        # 排序并返回TopN
        recommendations = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_n]

        return recommendations


if __name__ == "__main__":
    # 测试协同过滤
    # 创建测试数据
    data = {
        'item1': [5, 3, 4, 4, 0],
        'item2': [3, 1, 2, 3, 3],
        'item3': [4, 2, 4, 0, 2],
        'item4': [4, 3, 3, 5, 4],
        'item5': [0, 5, 2, 4, 5]
    }
    user_item_matrix = pd.DataFrame(data, index=['user1', 'user2', 'user3', 'user4', 'user5'])

    # 测试UserCF
    user_cf = UserCF(n_neighbors=3, top_n=3)
    user_cf.fit(user_item_matrix)
    recs = user_cf.recommend('user1')
    print(f"UserCF推荐: {recs}")

    # 测试ItemCF
    item_cf = ItemCF(n_neighbors=3, top_n=3)
    item_cf.fit(user_item_matrix)
    recs = item_cf.recommend('user1')
    print(f"ItemCF推荐: {recs}")

    # 测试相似物品
    sim_items = item_cf.get_similar_items('item1', top_n=2)
    print(f"相似物品: {sim_items}")
