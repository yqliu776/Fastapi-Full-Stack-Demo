from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field
import time
from datetime import datetime


class ResponseModel(BaseModel):
    """统一API响应模型
    
    定义了API响应的标准格式，包含状态码、消息、数据和时间戳。
    
    Attributes:
        code: HTTP状态码
        message: 响应消息
        data: 响应数据
        timestamp: 响应时间戳(秒)
    """
    code: int = Field(200, description="状态码")
    message: str = Field("操作成功", description="返回消息")
    data: Any = Field(None, description="返回数据")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="时间戳")
    
    class Config:
        arbitrary_types_allowed = True
