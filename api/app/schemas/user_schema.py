"""
用户相关Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求模型 ====================

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[int] = Field(None, ge=0, le=2, description="性别：0-未知 1-男 2-女")
    grade: Optional[str] = Field(None, max_length=20, description="年级")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    campus: Optional[str] = Field(None, max_length=50, description="校区")


class PasswordUpdate(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class RealNameApply(BaseModel):
    """实名认证申请"""
    real_name: str = Field(..., max_length=50, description="真实姓名")
    student_id: str = Field(..., max_length=50, description="学号")
    id_card: Optional[str] = Field(None, max_length=50, description="身份证号")
    student_card_front: str = Field(..., max_length=255, description="学生证正面照")
    student_card_back: str = Field(..., max_length=255, description="学生证反面照")


# ==================== 响应模型 ====================

class UserInfo(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    gender: int = 0
    grade: Optional[str] = None
    major: Optional[str] = None
    campus: Optional[str] = None
    status: int = 0
    user_level: int = 1
    is_real_name: int = 0
    create_time: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserLoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_info: UserInfo


class UserDetail(BaseModel):
    """用户详情（公开）"""
    id: int
    username: str
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    gender: int = 0
    grade: Optional[str] = None
    major: Optional[str] = None
    campus: Optional[str] = None
    user_level: int = 1
    is_real_name: int = 0

    class Config:
        orm_mode = True
