from pydantic import BaseModel, EmailStr, field_validator, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_schema import BaseSchema, TimestampMixin, PaginationParams


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


class UserBase(BaseModel):
    """用户基础模型"""
    
    user_name: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    phone_number: Optional[str] = Field(None, description="手机号码")


class UserCreate(UserBase):
    """用户创建模型（用于用户注册）"""
    
    password: str = Field(..., min_length=6, description="用户密码")
    
    @classmethod
    @field_validator("user_name")
    def username_alphanumeric(cls, v):
        """验证用户名只包含字母、数字和下划线"""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserAdminCreate(UserCreate):
    """管理员创建用户模型（包含角色指定）"""
    
    role_codes: List[str] = Field(..., min_items=1, description="角色代码列表")


class UserUpdate(BaseModel):
    """用户更新模型"""
    
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    role_codes: Optional[List[str]] = None
    
    model_config = {
        "from_attributes": True
    }


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


class UserResponse(UserBase, TimestampMixin):
    """用户基本信息响应模型"""
    
    id: int
    
    model_config = {
        "from_attributes": True
    }


class UserResponseWithRoles(UserResponse):
    """带角色信息的用户响应模型"""
    
    roles: List[RoleInfo] = []
    
    @classmethod
    def from_orm(cls, obj: Any) -> "UserResponseWithRoles":
        """从ORM模型创建响应模型"""
        # 创建基本用户信息
        user_data = {
            "id": obj.id,
            "user_name": obj.user_name,
            "email": obj.email,
            "phone_number": obj.phone_number,
            "creation_date": obj.creation_date,
            "last_update_date": obj.last_update_date,
            "roles": []
        }
        
        # 如果有角色信息，则添加
        if hasattr(obj, "roles") and obj.roles:
            user_data["roles"] = [
                {
                    "id": role.id, 
                    "role_name": role.role_name, 
                    "role_code": role.role_code
                } 
                for role in obj.roles
            ]
        
        return cls(**user_data)


class UserFilter(PaginationParams):
    """用户过滤参数"""
    
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None 


class UserRoleAssign(BaseModel):
    """用户角色分配请求模型"""
    
    role_codes: List[str] = Field(..., min_items=1, description="角色代码列表")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "role_codes": ["admin", "user"]
            }
        }
    } 


class UserRoleRemove(BaseModel):
    """用户角色删除请求模型"""
    
    role_codes: List[str] = Field(..., min_items=1, description="要删除的角色代码列表")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "role_codes": ["admin"]
            }
        }
    } 