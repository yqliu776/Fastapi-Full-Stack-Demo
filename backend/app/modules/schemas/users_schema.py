from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# 基础模型
class BaseSchema(BaseModel):
    id: Optional[int] = None
    
    class Config:
        orm_mode = True


# 用户模型
class UserBase(BaseModel):
    user_name: str = Field(..., description="用户名")
    phone_number: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")


class UserCreate(UserBase):
    password: str = Field(..., description="密码")


class UserUpdate(BaseSchema):
    user_name: Optional[str] = Field(None, description="用户名")
    phone_number: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    password: Optional[str] = Field(None, description="密码")


class UserResponse(UserBase, BaseSchema):
    created_by: str
    creation_date: datetime
    
    class Config:
        orm_mode = True


# 角色模型
class RoleBase(BaseModel):
    role_name: str = Field(..., description="角色名称")
    role_code: str = Field(..., description="角色编码")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    role_name: Optional[str] = Field(None, description="角色名称")
    role_code: Optional[str] = Field(None, description="角色编码")


class RoleResponse(RoleBase, BaseSchema):
    created_by: str
    creation_date: datetime
    
    class Config:
        orm_mode = True


# 权限模型
class PermissionBase(BaseModel):
    permission_name: str = Field(..., description="权限名称")
    permission_code: str = Field(..., description="权限编码")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseSchema):
    permission_name: Optional[str] = Field(None, description="权限名称")
    permission_code: Optional[str] = Field(None, description="权限编码")


class PermissionResponse(PermissionBase, BaseSchema):
    created_by: str
    creation_date: datetime
    
    class Config:
        orm_mode = True


# 菜单模型
class MenuBase(BaseModel):
    menu_name: str = Field(..., description="菜单名称")
    menu_code: str = Field(..., description="菜单编码")
    menu_path: Optional[str] = Field(None, description="菜单路径")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: Optional[int] = Field(0, description="显示顺序")


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseSchema):
    menu_name: Optional[str] = Field(None, description="菜单名称")
    menu_code: Optional[str] = Field(None, description="菜单编码")
    menu_path: Optional[str] = Field(None, description="菜单路径")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: Optional[int] = Field(None, description="显示顺序")


class MenuResponse(MenuBase, BaseSchema):
    created_by: str
    creation_date: datetime
    
    class Config:
        orm_mode = True


# 关联模型
class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int


class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int


class RoleMenuCreate(BaseModel):
    role_id: int
    menu_id: int 