from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .base_schema import BaseResponseModel


class ApiPermissionBase(BaseModel):
    """API权限绑定基础模型"""

    method: str = Field(..., description="HTTP方法", example="GET")
    path_pattern: str = Field(..., description="API路径模式", example="/users/list")
    permission_code: str = Field(..., description="权限编码", example="USER_MANAGE")
    description: Optional[str] = Field(None, description="说明")
    enabled: bool = Field(True, description="是否启用")

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        return value.upper()


class ApiPermissionCreate(ApiPermissionBase):
    """创建API权限绑定模型"""

    created_by: str = Field(..., description="创建人")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")


class ApiPermissionUpdate(BaseModel):
    """更新API权限绑定模型"""

    method: Optional[str] = Field(None, description="HTTP方法")
    path_pattern: Optional[str] = Field(None, description="API路径模式")
    permission_code: Optional[str] = Field(None, description="权限编码")
    description: Optional[str] = Field(None, description="说明")
    enabled: Optional[bool] = Field(None, description="是否启用")
    last_updated_by: str = Field(..., description="最后更新人")
    last_update_login: str = Field(..., description="最后登录ID")

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: Optional[str]) -> Optional[str]:
        return value.upper() if value else value


class ApiPermissionResponse(ApiPermissionBase, BaseResponseModel):
    """API权限绑定响应模型"""

    id: int = Field(..., description="绑定ID")
    creation_date: datetime = Field(..., description="创建时间")
    last_update_date: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True


class ApiPermissionBatchResponse(BaseResponseModel):
    """API权限绑定列表响应模型"""

    items: List[ApiPermissionResponse] = Field(..., description="绑定列表")
    total: int = Field(..., description="总记录数")
