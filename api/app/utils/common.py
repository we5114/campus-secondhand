"""
通用工具函数
"""
import uuid
import time
import random
import string
from datetime import datetime
from typing import Optional


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4()).replace("-", "")


def generate_order_no(prefix: str = "ORD") -> str:
    """
    生成订单号

    Args:
        prefix: 订单号前缀

    Returns:
        订单号字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"


def generate_refund_no() -> str:
    """生成退款单号"""
    return generate_order_no("REF")


def get_current_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def get_current_datetime() -> str:
    """获取当前日期时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date() -> str:
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(dt: Optional[datetime]) -> Optional[str]:
    """格式化日期"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


def mask_phone(phone: str) -> str:
    """
    手机号脱敏

    Args:
        phone: 手机号

    Returns:
        脱敏后的手机号
    """
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def mask_email(email: str) -> str:
    """
    邮箱脱敏

    Args:
        email: 邮箱

    Returns:
        脱敏后的邮箱
    """
    if not email or "@" not in email:
        return email
    username, domain = email.split("@", 1)
    if len(username) <= 2:
        return username + "***" + "@" + domain
    return username[0] + "***" + username[-1] + "@" + domain


def mask_id_card(id_card: str) -> str:
    """
    身份证号脱敏

    Args:
        id_card: 身份证号

    Returns:
        脱敏后的身份证号
    """
    if not id_card or len(id_card) < 10:
        return id_card
    return id_card[:6] + "********" + id_card[-4:]


def calculate_page(total: int, page_size: int) -> int:
    """
    计算总页数

    Args:
        total: 总记录数
        page_size: 每页数量

    Returns:
        总页数
    """
    if page_size <= 0:
        return 0
    return (total + page_size - 1) // page_size


def safe_int(value, default: int = 0) -> int:
    """
    安全转换为整数

    Args:
        value: 待转换的值
        default: 默认值

    Returns:
        转换后的整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """
    安全转换为浮点数

    Args:
        value: 待转换的值
        default: 默认值

    Returns:
        转换后的浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串

    Args:
        s: 原字符串
        max_length: 最大长度
        suffix: 后缀

    Returns:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def list_to_tree(items: list, id_key: str = "id", parent_key: str = "parent_id", children_key: str = "children") -> list:
    """
    将列表转换为树形结构

    Args:
        items: 列表数据
        id_key: ID字段名
        parent_key: 父ID字段名
        children_key: 子节点字段名

    Returns:
        树形结构列表
    """
    # 创建ID到节点的映射
    item_map = {item[id_key]: item for item in items}

    # 构建树
    roots = []
    for item in items:
        parent_id = item.get(parent_key, 0)
        if parent_id == 0 or parent_id not in item_map:
            roots.append(item)
        else:
            parent = item_map[parent_id]
            if children_key not in parent:
                parent[children_key] = []
            parent[children_key].append(item)

    return roots
