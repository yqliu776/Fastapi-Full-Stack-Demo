from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime

from .base_schema import BaseSchema


class RoleInfo(BaseSchema):
    """角色信息模型"""
    role_name: str
    role_code: str


class PermissionInfo(BaseSchema):
    """权限信息模型"""
    permission_name: str
    permission_code: str


class MenuInfo(BaseSchema):
    """菜单信息模型"""
    menu_name: str
    menu_code: str
    menu_path: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class UserBase(BaseSchema):
    """用户基础信息模型"""
    user_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., description="密码")

    @classmethod
    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")
        # 可以添加其他密码强度验证
        return v

    @classmethod
    @field_validator("user_name")
    def username_format(cls, v):
        if len(v) < 3:
            raise ValueError("用户名长度不能少于3位")
        if not v.isalnum():
            raise ValueError("用户名只能包含字母和数字")
        return v

    @classmethod
    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("手机号只能包含数字")
        return v


class UserUpdate(BaseSchema):
    """用户更新模型"""
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @classmethod
    @field_validator("user_name")
    def username_format(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("用户名长度不能少于3位")
            if not v.isalnum():
                raise ValueError("用户名只能包含字母和数字")
        return v

    @classmethod
    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("手机号只能包含数字")
        return v


class UserDetail(UserBase):
    """用户详情模型"""
    id: int
    creation_date: datetime
    last_update_date: datetime
    roles: List[RoleInfo] = []


class UserList(BaseModel):
    """用户列表模型"""
    items: List[UserDetail]
    total: int
    page: int
    size: int 