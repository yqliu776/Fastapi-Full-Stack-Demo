from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .base_schema import BaseResponseModel


class PermissionBase(BaseModel):
    """权限基础模型"""
    permission_name: str = Field(..., description="权限名称", example="用户管理")
    permission_code: str = Field(..., description="权限代码", example="USER_MANAGE")


class PermissionCreate(PermissionBase):
    """权限创建模型"""
    created_by: str = Field(..., description="创建人")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class PermissionUpdate(BaseModel):
    """权限更新模型"""
    permission_name: Optional[str] = Field(None, description="权限名称", example="用户管理")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class PermissionResponse(PermissionBase, BaseResponseModel):
    """权限响应模型"""
    id: int = Field(..., description="权限ID")
    creation_date: datetime = Field(..., description="创建时间")
    last_update_date: datetime = Field(..., description="最后更新时间")
    
    class Config:
        from_attributes = True


class PermissionDetail(PermissionResponse):
    """权限详情响应模型"""
    roles: Optional[List[dict]] = Field(None, description="拥有该权限的角色列表")


class PermissionBatchResponse(BaseResponseModel):
    """权限批量操作响应模型"""
    items: List[PermissionResponse] = Field(..., description="权限列表")
    total: int = Field(..., description="总记录数") 