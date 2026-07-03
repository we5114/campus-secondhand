"""
用户服务层
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.user import User, Admin, UserRealName, UserAddress
from app.schemas.user_schema import UserRegister, UserUpdate, PasswordUpdate, RealNameApply
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.config.constants import ErrorCode, UserStatus
from app.utils.common import generate_order_no


class UserService:
    """用户服务类"""

    @staticmethod
    def register(db: Session, user_data: UserRegister) -> dict:
        """
        用户注册

        Args:
            db: 数据库会话
            user_data: 用户注册数据

        Returns:
            注册结果

        Raises:
            BusinessException: 注册失败时抛出
        """
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise BusinessException(ErrorCode.USER_ALREADY_EXISTS, "用户名已存在")

        # 检查手机号是否已存在
        if user_data.phone:
            existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
            if existing_phone:
                raise BusinessException(ErrorCode.USER_PHONE_EXISTS, "手机号已被注册")

        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise BusinessException(ErrorCode.USER_EMAIL_EXISTS, "邮箱已被注册")

        # 创建用户
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            password=hashed_password,
            phone=user_data.phone,
            email=user_data.email,
            nickname=user_data.nickname or user_data.username
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 生成token
        token = create_access_token(new_user.id)

        return {
            "token": token,
            "user_info": new_user.to_dict()
        }

    @staticmethod
    def login(db: Session, username: str, password: str) -> dict:
        """
        用户登录

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            登录结果
        """
        # 查询用户
        user = db.query(User).filter(
            or_(User.username == username, User.phone == username, User.email == username)
        ).first()

        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        # 检查状态
        if user.status != UserStatus.NORMAL:
            raise BusinessException(ErrorCode.USER_DISABLED, "账号已被禁用")

        # 验证密码
        if not verify_password(password, user.password):
            raise BusinessException(ErrorCode.USER_PASSWORD_ERROR, "密码错误")

        # 更新登录信息
        user.last_login_time = func.now()
        db.commit()

        # 生成token
        token = create_access_token(user.id)

        return {
            "token": token,
            "user_info": user.to_dict()
        }

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def admin_login(db: Session, username: str, password: str) -> dict:
        """
        管理员登录

        Args:
            db: 数据库会话
            username: 管理员用户名
            password: 密码

        Returns:
            登录结果
        """
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "管理员账号不存在")

        if admin.status != 0:
            raise BusinessException(ErrorCode.USER_DISABLED, "管理员账号已被禁用")

        if not verify_password(password, admin.password):
            raise BusinessException(ErrorCode.USER_PASSWORD_ERROR, "密码错误")

        admin.last_login_time = func.now()
        db.commit()
        db.refresh(admin)

        token = create_access_token(admin.id)

        return {
            "token": token,
            "user_info": {
                "id": admin.id,
                "username": admin.username,
                "nickname": admin.nickname or "超级管理员",
                "role_id": admin.role_id,
                "is_admin": True
            }
        }

    @staticmethod
    def get_user_info(db: Session, user_id: int) -> dict:
        """
        获取用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户信息
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        return user.to_dict()

    @staticmethod
    def update_user_info(db: Session, user_id: int, update_data: UserUpdate) -> dict:
        """
        更新用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            update_data: 更新数据

        Returns:
            更新后的用户信息
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        # 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user.to_dict()

    @staticmethod
    def update_password(db: Session, user_id: int, password_data: PasswordUpdate) -> bool:
        """
        修改密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            password_data: 密码数据

        Returns:
            是否成功
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        # 验证旧密码
        if not verify_password(password_data.old_password, user.password):
            raise BusinessException(ErrorCode.USER_PASSWORD_ERROR, "原密码错误")

        # 更新密码
        user.password = hash_password(password_data.new_password)
        db.commit()

        return True

    @staticmethod
    def apply_real_name(db: Session, user_id: int, real_name_data: RealNameApply) -> dict:
        """
        申请实名认证

        Args:
            db: 数据库会话
            user_id: 用户ID
            real_name_data: 实名认证数据

        Returns:
            申请结果
        """
        # 检查是否已申请
        existing = db.query(UserRealName).filter(UserRealName.user_id == user_id).first()

        if existing:
            # 更新申请
            existing.real_name = real_name_data.real_name
            existing.student_id = real_name_data.student_id
            existing.id_card = real_name_data.id_card
            existing.student_card_front = real_name_data.student_card_front
            existing.student_card_back = real_name_data.student_card_back
            existing.status = 0  # 重置为待审核
            db.commit()
            db.refresh(existing)
            return existing.to_dict()
        else:
            # 新建申请
            new_real_name = UserRealName(
                user_id=user_id,
                real_name=real_name_data.real_name,
                student_id=real_name_data.student_id,
                id_card=real_name_data.id_card,
                student_card_front=real_name_data.student_card_front,
                student_card_back=real_name_data.student_card_back
            )
            db.add(new_real_name)
            db.commit()
            db.refresh(new_real_name)
            return new_real_name.to_dict()

    @staticmethod
    def get_user_detail(db: Session, user_id: int) -> dict:
        """
        获取用户详情（公开信息）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户详情
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        # 返回公开信息
        return {
            "id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "nickname": user.nickname,
            "gender": user.gender,
            "grade": user.grade,
            "major": user.major,
            "campus": user.campus,
            "user_level": user.user_level,
            "is_real_name": user.is_real_name
        }


class BusinessException(Exception):
    """业务异常类"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
