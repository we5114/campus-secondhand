"""
用户相关数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Text
from sqlalchemy.sql import func

from app.models import BaseModel


class User(BaseModel):
    """用户表"""
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    phone = Column(String(20), nullable=True, unique=True, comment="手机号")
    email = Column(String(100), nullable=True, unique=True, comment="邮箱")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    nickname = Column(String(50), nullable=True, comment="昵称")
    gender = Column(SmallInteger, default=0, comment="性别：0-未知 1-男 2-女")
    grade = Column(String(20), nullable=True, comment="年级")
    major = Column(String(100), nullable=True, comment="专业")
    campus = Column(String(50), nullable=True, comment="校区")
    status = Column(SmallInteger, default=0, comment="状态：0-正常 1-禁用 2-注销")
    user_level = Column(SmallInteger, default=1, comment="用户等级：1-普通用户 2-VIP用户")
    is_real_name = Column(SmallInteger, default=0, comment="是否实名认证：0-否 1-是")
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class UserRealName(BaseModel):
    """用户实名认证表"""
    __tablename__ = "user_real_name"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(BigInteger, nullable=False, unique=True, comment="用户ID")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    student_id = Column(String(50), nullable=False, comment="学号")
    id_card = Column(String(50), nullable=True, comment="身份证号（脱敏）")
    student_card_front = Column(String(255), nullable=True, comment="学生证正面照")
    student_card_back = Column(String(255), nullable=True, comment="学生证反面照")
    status = Column(SmallInteger, default=0, comment="审核状态：0-待审核 1-通过 2-拒绝")
    audit_user_id = Column(BigInteger, nullable=True, comment="审核人ID")
    audit_time = Column(DateTime, nullable=True, comment="审核时间")
    audit_remark = Column(String(255), nullable=True, comment="审核备注")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class UserAddress(BaseModel):
    """用户地址表"""
    __tablename__ = "user_address"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="地址ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    receiver = Column(String(50), nullable=False, comment="收货人")
    phone = Column(String(20), nullable=False, comment="联系电话")
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=True, comment="城市")
    district = Column(String(50), nullable=True, comment="区县")
    detail = Column(String(255), nullable=False, comment="详细地址")
    is_default = Column(SmallInteger, default=0, comment="是否默认：0-否 1-是")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Admin(BaseModel):
    """管理员表"""
    __tablename__ = "admin"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="管理员ID")
    username = Column(String(50), nullable=False, unique=True, comment="管理员用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    role_id = Column(SmallInteger, default=1, comment="角色ID：1-超级管理员 2-普通管理员")
    status = Column(SmallInteger, default=0, comment="状态：0-正常 1-禁用")
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
