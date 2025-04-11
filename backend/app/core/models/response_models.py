from typing import Any, Dict, Optional, Union, Generic, TypeVar, List
from pydantic import BaseModel, Field
from datetime import datetime
import time

T = TypeVar('T')

class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型
    
    Attributes:
        items: 数据列表
        total: 总记录数
    """
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总记录数")

class ResponseModel(BaseModel):
    """统一API响应模型
    
    定义了API响应的标准格式，包含状态码、消息、数据和时间戳。
    
    Attributes:
        code: HTTP状态码
        message: 响应消息
        data: 响应数据
        timestamp: 响应时间戳(秒)
        process_time: 处理时间(秒)
    """
    code: int = Field(200, description="状态码")
    message: str = Field("操作成功", description="返回消息")
    data: Any = Field(None, description="返回数据")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="时间戳")
    process_time: float = Field(0.0, description="处理时间(秒)")
    
    model_config = {
        "arbitrary_types_allowed": True
    }

    @classmethod
    def success(cls, data: Any = None, message: str = "操作成功", process_time: float = 0.0) -> "ResponseModel":
        """创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            process_time: 处理时间
            
        Returns:
            ResponseModel: 成功响应实例
        """
        return cls(
            code=200,
            message=message,
            data=data,
            process_time=process_time
        )
    
    @classmethod
    def error(cls, code: int = 400, message: str = "操作失败", data: Any = None, process_time: float = 0.0) -> "ResponseModel":
        """创建错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            data: 错误数据
            process_time: 处理时间
            
        Returns:
            ResponseModel: 错误响应实例
        """
        return cls(
            code=code,
            message=message,
            data=data,
            process_time=process_time
        )
    
    @classmethod
    def paginated(cls, items: List[Any], total: int, message: str = "获取列表成功", process_time: float = 0.0) -> "ResponseModel":
        """创建分页数据响应
        
        Args:
            items: 数据列表
            total: 总记录数
            message: 响应消息
            process_time: 处理时间
            
        Returns:
            ResponseModel: 分页数据响应实例
        """
        return cls(
            code=200,
            message=message,
            data=PaginatedData(items=items, total=total),
            process_time=process_time
        )
