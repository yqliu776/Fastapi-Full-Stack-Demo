from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.modules.schemas.base_schema import BaseResponseModel


class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., description="角色名称", example="系统管理员")
    role_code: str = Field(..., description="角色代码", example="ROLE_ADMIN")


class RoleCreate(RoleBase):
    """角色创建模型"""
    created_by: str = Field(..., description="创建人")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class RoleUpdate(BaseModel):
    """角色更新模型"""
    role_name: Optional[str] = Field(None, description="角色名称", example="系统管理员")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class RoleResponse(RoleBase, BaseResponseModel):
    """角色响应模型"""
    id: int = Field(..., description="角色ID")
    creation_date: datetime = Field(..., description="创建时间")
    last_update_date: datetime = Field(..., description="最后更新时间")
    
    class Config:
        from_attributes = True


class RoleDetail(RoleResponse):
    """角色详情响应模型"""
    permissions: Optional[List[dict]] = Field(None, description="角色拥有的权限列表")
    menus: Optional[List[dict]] = Field(None, description="角色拥有的菜单列表")


class RoleBatchResponse(BaseResponseModel):
    """角色批量操作响应模型"""
    items: List[RoleResponse] = Field(..., description="角色列表")
    total: int = Field(..., description="总记录数")


class RolePermissionOperation(BaseModel):
    """角色权限操作模型"""
    role_id: int = Field(..., description="角色ID")
    permission_ids: List[int] = Field(..., description="权限ID列表")
    operator: str = Field(..., description="操作人")
    operation_login: str = Field(..., description="操作登录ID")


class RoleMenuOperation(BaseModel):
    """角色菜单操作模型"""
    role_id: int = Field(..., description="角色ID")
    menu_ids: List[int] = Field(..., description="菜单ID列表")
    operator: str = Field(..., description="操作人")
    operation_login: str = Field(..., description="操作登录ID") 