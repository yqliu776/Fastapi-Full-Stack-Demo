from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar, List
from datetime import datetime


class BaseSchema(BaseModel):
    """
    基础模型，为所有模型提供通用配置
    """
    
    model_config = {
        "from_attributes": True,  # 支持ORM模型映射
        "validate_assignment": True,  # 赋值时验证
        "arbitrary_types_allowed": True,  # 允许使用任意类型
        "json_encoders": {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None
        }
    }


class TimestampMixin(BaseModel):
    """
    时间戳混入类，提供创建和更新时间字段
    """
    creation_date: Optional[datetime] = None
    last_update_date: Optional[datetime] = None


class PaginationParams(BaseModel):
    """
    分页参数模型
    """
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页大小")
    
    @property
    def skip(self) -> int:
        """
        计算跳过的记录数
        """
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """
        获取限制数
        """
        return self.size


class BaseResponseModel(BaseModel):
    """基础响应模型，用于统一API响应格式"""
    
    # Pydantic V2 风格
    model_config = {
        "from_attributes": True
    }

    