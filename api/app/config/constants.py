"""
常量定义模块
"""
from enum import IntEnum, Enum


# ==================== 用户相关常量 ====================

class UserStatus(IntEnum):
    """用户状态"""
    NORMAL = 0  # 正常
    DISABLED = 1  # 禁用
    DELETED = 2  # 注销


class GenderType(IntEnum):
    """性别类型"""
    UNKNOWN = 0  # 未知
    MALE = 1  # 男
    FEMALE = 2  # 女


class UserLevel(IntEnum):
    """用户等级"""
    NORMAL = 1  # 普通用户
    VIP = 2  # VIP用户


class RealNameStatus(IntEnum):
    """实名认证状态"""
    PENDING = 0  # 待审核
    APPROVED = 1  # 通过
    REJECTED = 2  # 拒绝


# ==================== 商品相关常量 ====================

class ProductStatus(IntEnum):
    """商品状态"""
    ON_SHELF = 0  # 上架
    SOLD = 1  # 已售
    OFF_SHELF = 2  # 下架
    AUDITING = 3  # 审核中
    VIOLATION = 4  # 违规


class ProductCondition(IntEnum):
    """商品成色"""
    NEW = 1  # 全新
    NINETY_PERCENT = 2  # 九成新
    EIGHTY_PERCENT = 3  # 八成新
    SEVENTY_PERCENT = 4  # 七成新
    OTHER = 5  # 其他


class TradeType(IntEnum):
    """交易方式"""
    FACE_TO_FACE = 1  # 面交
    MAIL = 2  # 邮寄
    BOTH = 3  # 均可


class AuditStatus(IntEnum):
    """审核状态"""
    PENDING = 0  # 待审核
    APPROVED = 1  # 通过
    REJECTED = 2  # 拒绝


# ==================== 订单相关常量 ====================

class OrderStatus(IntEnum):
    """订单状态"""
    PENDING_PAYMENT = 0  # 待付款
    PENDING_SHIPMENT = 1  # 待发货
    PENDING_RECEIPT = 2  # 待收货
    COMPLETED = 3  # 已完成
    CANCELLED = 4  # 已取消
    REFUNDING = 5  # 退款中
    REFUNDED = 6  # 已退款


class PayType(IntEnum):
    """支付方式"""
    UNPAID = 0  # 未支付
    WECHAT = 1  # 微信
    ALIPAY = 2  # 支付宝
    OFFLINE = 3  # 线下支付


class RefundStatus(IntEnum):
    """退款状态"""
    PENDING = 0  # 待处理
    APPROVED = 1  # 同意
    REJECTED = 2  # 拒绝
    PROCESSING = 3  # 退款中
    COMPLETED = 4  # 已完成


# ==================== 消息相关常量 ====================

class MessageType(IntEnum):
    """消息类型"""
    SYSTEM = 1  # 系统通知
    ORDER = 2  # 订单消息
    INTERACTION = 3  # 互动消息
    ACTIVITY = 4  # 活动消息


class ChatMsgType(IntEnum):
    """聊天消息类型"""
    TEXT = 1  # 文本
    IMAGE = 2  # 图片
    VOICE = 3  # 语音
    SYSTEM = 4  # 系统消息


# ==================== 行为相关常量 ====================

class BehaviorType(str, Enum):
    """用户行为类型"""
    VIEW = "view"  # 浏览
    CLICK = "click"  # 点击
    FAVORITE = "favorite"  # 收藏
    CART = "cart"  # 加购
    BUY = "buy"  # 购买


# 行为权重
BEHAVIOR_WEIGHT = {
    BehaviorType.VIEW.value: 1,
    BehaviorType.CLICK.value: 2,
    BehaviorType.FAVORITE.value: 5,
    BehaviorType.CART.value: 8,
    BehaviorType.BUY.value: 10,
}


# ==================== 错误码常量 ====================

class ErrorCode:
    """错误码定义"""

    # 成功
    SUCCESS = 0

    # 通用错误 10000-19999
    PARAM_ERROR = 10001
    SYSTEM_ERROR = 10002
    UNAUTHORIZED = 10003
    FORBIDDEN = 10004
    NOT_FOUND = 10005
    METHOD_NOT_ALLOWED = 10006
    TOO_MANY_REQUESTS = 10007

    # 用户相关 20000-29999
    USER_NOT_FOUND = 20001
    USER_ALREADY_EXISTS = 20002
    USER_PASSWORD_ERROR = 20003
    USER_DISABLED = 20004
    USER_NOT_LOGIN = 20005
    USER_TOKEN_EXPIRED = 20006
    USER_TOKEN_INVALID = 20007
    USER_PHONE_EXISTS = 20008
    USER_EMAIL_EXISTS = 20009

    # 商品相关 30000-39999
    PRODUCT_NOT_FOUND = 30001
    PRODUCT_OFF_SHELF = 30002
    PRODUCT_SOLD_OUT = 30003
    PRODUCT_NOT_BELONG = 30004
    CATEGORY_NOT_FOUND = 30005

    # 订单相关 40000-49999
    ORDER_NOT_FOUND = 40001
    ORDER_STATUS_ERROR = 40002
    ORDER_NOT_BELONG = 40003
    ORDER_CANCEL_FAILED = 40004
    REFUND_NOT_FOUND = 40005

    # 消息相关 50000-59999
    MESSAGE_NOT_FOUND = 50001

    # 文件相关 60000-69999
    FILE_UPLOAD_FAILED = 60001
    FILE_TOO_LARGE = 60002
    FILE_TYPE_NOT_ALLOWED = 60003

    # 大模型相关 70000-79999
    LLM_SERVICE_ERROR = 70001


# 错误消息映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "success",
    ErrorCode.PARAM_ERROR: "参数错误",
    ErrorCode.SYSTEM_ERROR: "系统错误",
    ErrorCode.UNAUTHORIZED: "未授权",
    ErrorCode.FORBIDDEN: "无权限访问",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.METHOD_NOT_ALLOWED: "请求方法不允许",
    ErrorCode.TOO_MANY_REQUESTS: "请求过于频繁",
    ErrorCode.USER_NOT_FOUND: "用户不存在",
    ErrorCode.USER_ALREADY_EXISTS: "用户名已存在",
    ErrorCode.USER_PASSWORD_ERROR: "密码错误",
    ErrorCode.USER_DISABLED: "账号已被禁用",
    ErrorCode.USER_NOT_LOGIN: "用户未登录",
    ErrorCode.USER_TOKEN_EXPIRED: "Token已过期",
    ErrorCode.USER_TOKEN_INVALID: "Token无效",
    ErrorCode.USER_PHONE_EXISTS: "手机号已被注册",
    ErrorCode.USER_EMAIL_EXISTS: "邮箱已被注册",
    ErrorCode.PRODUCT_NOT_FOUND: "商品不存在",
    ErrorCode.PRODUCT_OFF_SHELF: "商品已下架",
    ErrorCode.PRODUCT_SOLD_OUT: "商品已售出",
    ErrorCode.PRODUCT_NOT_BELONG: "无权限操作该商品",
    ErrorCode.CATEGORY_NOT_FOUND: "分类不存在",
    ErrorCode.ORDER_NOT_FOUND: "订单不存在",
    ErrorCode.ORDER_STATUS_ERROR: "订单状态错误",
    ErrorCode.ORDER_NOT_BELONG: "无权限查看该订单",
    ErrorCode.ORDER_CANCEL_FAILED: "订单取消失败",
    ErrorCode.REFUND_NOT_FOUND: "退款申请不存在",
    ErrorCode.MESSAGE_NOT_FOUND: "消息不存在",
    ErrorCode.FILE_UPLOAD_FAILED: "文件上传失败",
    ErrorCode.FILE_TOO_LARGE: "文件过大",
    ErrorCode.FILE_TYPE_NOT_ALLOWED: "不支持的文件类型",
    ErrorCode.LLM_SERVICE_ERROR: "大模型服务异常",
}


# ==================== 其他常量 ====================

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"}

# 允许的文件类型
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | {"application/pdf", "text/plain"}

# 商品图片最大数量
MAX_PRODUCT_IMAGES = 9

# 推荐商品数量
DEFAULT_RECOMMEND_COUNT = 20

# 热门商品数量
DEFAULT_HOT_COUNT = 10
