from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import List, Optional


class TokenPayload(BaseModel):
    """令牌负载模型"""
    sub: str
    exp: datetime
    roles: List[str] = []
    permissions: List[str] = []


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    session_id: Optional[str] = Field(None, description="会话ID")


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

    @classmethod
    @field_validator("username")
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("用户名不能为空")
        return v

    @classmethod
    @field_validator("password")
    def password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("密码不能为空")
        return v


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: int = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户名")
    permissions: list = Field(..., description="权限列表")


class PasswordChangeRequest(BaseModel):
    """密码修改请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., description="新密码")
    confirm_password: str = Field(..., description="确认密码")

    @classmethod
    @field_validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")
        # 这里可以添加更多的密码强度验证逻辑
        return v

    @classmethod
    @field_validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values.data and v != values.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v 