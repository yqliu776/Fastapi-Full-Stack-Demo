from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.modules.schemas.base_schema import BaseResponseModel


class MenuBase(BaseModel):
    """菜单基础模型"""
    menu_name: str = Field(..., description="菜单名称", example="系统管理")
    menu_code: str = Field(..., description="菜单代码", example="SYSTEM")
    menu_path: str = Field(..., description="菜单路径", example="/system")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: Optional[int] = Field(0, description="排序号")


class MenuCreate(MenuBase):
    """菜单创建模型"""
    created_by: str = Field(..., description="创建人")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class MenuUpdate(BaseModel):
    """菜单更新模型"""
    menu_name: Optional[str] = Field(None, description="菜单名称", example="系统管理")
    menu_path: Optional[str] = Field(None, description="菜单路径", example="/system")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: Optional[int] = Field(None, description="排序号")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class MenuResponse(MenuBase, BaseResponseModel):
    """菜单响应模型"""
    id: int = Field(..., description="菜单ID")
    creation_date: datetime = Field(..., description="创建时间")
    last_update_date: datetime = Field(..., description="最后更新时间")
    
    class Config:
        from_attributes = True


class MenuDetail(MenuResponse):
    """菜单详情响应模型"""
    roles: Optional[List[dict]] = Field(None, description="拥有该菜单的角色列表")
    children: Optional[List['MenuDetail']] = Field(None, description="子菜单列表")


# 解决类型循环引用问题
MenuDetail.update_forward_refs()


class MenuTreeNode(BaseModel):
    """菜单树节点模型"""
    id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_code: str = Field(..., description="菜单代码")
    menu_path: str = Field(..., description="菜单路径")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: int = Field(0, description="排序号")
    children: Optional[List['MenuTreeNode']] = Field(None, description="子菜单列表")
    
    class Config:
        from_attributes = True


# 解决类型循环引用问题
MenuTreeNode.update_forward_refs()


class MenuBatchResponse(BaseResponseModel):
    """菜单批量操作响应模型"""
    items: List[MenuResponse] = Field(..., description="菜单列表")
    total: int = Field(..., description="总记录数") 