"""
模型工具类
包含相似度计算、评估指标等工具函数
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_cosine_similarity(vec1, vec2):
    """
    计算余弦相似度

    Args:
        vec1: 向量1
        vec2: 向量2

    Returns:
        float: 相似度
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def calculate_pearson_correlation(vec1, vec2):
    """
    计算皮尔逊相关系数

    Args:
        vec1: 向量1
        vec2: 向量2

    Returns:
        float: 相关系数
    """
    if len(vec1) != len(vec2):
        raise ValueError("向量长度必须相同")

    # 只考虑两个向量都有值的位置
    mask = (vec1 != 0) & (vec2 != 0)
    if mask.sum() < 2:
        return 0.0

    vec1_filtered = vec1[mask]
    vec2_filtered = vec2[mask]

    # 计算均值
    mean1 = np.mean(vec1_filtered)
    mean2 = np.mean(vec2_filtered)

    # 中心化
    vec1_centered = vec1_filtered - mean1
    vec2_centered = vec2_filtered - mean2

    # 计算相关系数
    numerator = np.sum(vec1_centered * vec2_centered)
    denominator = np.sqrt(np.sum(vec1_centered ** 2)) * np.sqrt(np.sum(vec2_centered ** 2))

    if denominator == 0:
        return 0.0

    return numerator / denominator


def calculate_jaccard_similarity(set1, set2):
    """
    计算Jaccard相似度

    Args:
        set1: 集合1
        set2: 集合2

    Returns:
        float: 相似度
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 0.0

    return intersection / union


def calculate_rmse(predictions, actuals):
    """
    计算RMSE（均方根误差）

    Args:
        predictions: 预测值列表
        actuals: 实际值列表

    Returns:
        float: RMSE
    """
    if len(predictions) != len(actuals):
        raise ValueError("预测值和实际值长度必须相同")

    return math.sqrt(mean_squared_error(actuals, predictions))


def calculate_mae(predictions, actuals):
    """
    计算MAE（平均绝对误差）

    Args:
        predictions: 预测值列表
        actuals: 实际值列表

    Returns:
        float: MAE
    """
    if len(predictions) != len(actuals):
        raise ValueError("预测值和实际值长度必须相同")

    return mean_absolute_error(actuals, predictions)


def calculate_precision_recall(recommendations, actual_items, k=None):
    """
    计算精确率和召回率

    Args:
        recommendations: 推荐物品列表
        actual_items: 用户实际喜欢的物品列表
        k: TopK数量

    Returns:
        tuple: (precision, recall)
    """
    if k:
        recommendations = recommendations[:k]

    if not recommendations:
        return 0.0, 0.0

    rec_set = set(recommendations)
    actual_set = set(actual_items)

    # 计算交集
    intersection = rec_set & actual_set

    # 精确率：推荐中正确的比例
    precision = len(intersection) / len(rec_set) if rec_set else 0.0

    # 召回率：实际中被推荐的比例
    recall = len(intersection) / len(actual_set) if actual_set else 0.0

    return precision, recall


def calculate_ndcg(recommendations, actual_items, k=None):
    """
    计算NDCG（归一化折损累计增益）

    Args:
        recommendations: 推荐物品列表
        actual_items: 用户实际喜欢的物品列表
        k: TopK数量

    Returns:
        float: NDCG
    """
    if k:
        recommendations = recommendations[:k]

    if not recommendations:
        return 0.0

    actual_set = set(actual_items)

    # 计算DCG
    dcg = 0.0
    for i, item in enumerate(recommendations):
        if item in actual_set:
            dcg += 1.0 / math.log2(i + 2)  # i+2 因为从0开始

    # 计算IDCG（理想DCG）
    ideal_items = sorted(actual_items, key=lambda x: 1, reverse=True)[:len(recommendations)]
    idcg = 0.0
    for i, item in enumerate(ideal_items):
        idcg += 1.0 / math.log2(i + 2)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def calculate_hit_rate(recommendations, actual_items, k=None):
    """
    计算命中率

    Args:
        recommendations: 推荐物品列表
        actual_items: 用户实际喜欢的物品列表
        k: TopK数量

    Returns:
        float: 命中率
    """
    if k:
        recommendations = recommendations[:k]

    if not recommendations:
        return 0.0

    rec_set = set(recommendations)
    actual_set = set(actual_items)

    # 只要有一个命中就算命中
    hit = 1.0 if len(rec_set & actual_set) > 0 else 0.0

    return hit


def evaluate_recommendations(recommendations_dict, actual_dict, k_list=[10, 20, 50]):
    """
    评估推荐系统

    Args:
        recommendations_dict: 用户推荐结果字典 {user_id: [item_id, ...]}
        actual_dict: 用户实际喜欢的物品字典 {user_id: [item_id, ...]}
        k_list: TopK列表

    Returns:
        dict: 评估结果
    """
    results = {}

    for k in k_list:
        precisions = []
        recalls = []
        ndcgs = []
        hit_rates = []

        for user_id, recommendations in recommendations_dict.items():
            actual_items = actual_dict.get(user_id, [])

            if not actual_items:
                continue

            precision, recall = calculate_precision_recall(recommendations, actual_items, k)
            ndcg = calculate_ndcg(recommendations, actual_items, k)
            hit_rate = calculate_hit_rate(recommendations, actual_items, k)

            precisions.append(precision)
            recalls.append(recall)
            ndcgs.append(ndcg)
            hit_rates.append(hit_rate)

        results[f'Precision@{k}'] = np.mean(precisions) if precisions else 0.0
        results[f'Recall@{k}'] = np.mean(recalls) if recalls else 0.0
        results[f'NDCG@{k}'] = np.mean(ndcgs) if ndcgs else 0.0
        results[f'HitRate@{k}'] = np.mean(hit_rates) if hit_rates else 0.0

    return results


def normalize_scores(scores):
    """
    归一化分数到0-1

    Args:
        scores: 分数列表

    Returns:
        list: 归一化后的分数
    """
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [0.5] * len(scores)

    return [(score - min_score) / (max_score - min_score) for score in scores]


def load_user_item_matrix(data_path):
    """
    加载用户-物品评分矩阵

    Args:
        data_path: 数据路径

    Returns:
        DataFrame: 用户-物品评分矩阵
    """
    logger.info(f"加载用户-物品评分矩阵: {data_path}")

    # 读取数据
    df = pd.read_csv(data_path)

    # 转换为矩阵
    user_item_matrix = df.pivot_table(
        index='user_id',
        columns='product_id',
        values='score',
        fill_value=0
    )

    logger.info(f"用户-物品评分矩阵加载完成，形状: {user_item_matrix.shape}")
    return user_item_matrix


def save_model(model, model_path):
    """
    保存模型

    Args:
        model: 模型对象
        model_path: 模型保存路径
    """
    import pickle

    logger.info(f"保存模型: {model_path}")

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    logger.info("模型保存完成")


def load_model(model_path):
    """
    加载模型

    Args:
        model_path: 模型路径

    Returns:
        模型对象
    """
    import pickle

    logger.info(f"加载模型: {model_path}")

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    logger.info("模型加载完成")
    return model


if __name__ == "__main__":
    # 测试工具函数
    vec1 = np.array([1, 2, 3, 4, 5])
    vec2 = np.array([2, 3, 4, 5, 6])

    print(f"余弦相似度: {calculate_cosine_similarity(vec1, vec2)}")
    print(f"皮尔逊相关系数: {calculate_pearson_correlation(vec1, vec2)}")

    # 测试推荐评估
    recommendations = ['item1', 'item2', 'item3', 'item4', 'item5']
    actual_items = ['item2', 'item4', 'item6']

    precision, recall = calculate_precision_recall(recommendations, actual_items, k=5)
    print(f"精确率: {precision}, 召回率: {recall}")

    ndcg = calculate_ndcg(recommendations, actual_items, k=5)
    print(f"NDCG: {ndcg}")

    hit_rate = calculate_hit_rate(recommendations, actual_items, k=5)
    print(f"命中率: {hit_rate}")
