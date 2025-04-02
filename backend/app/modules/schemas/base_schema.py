from pydantic import BaseModel, Field
from typing import Optional, Any


class BaseSchema(BaseModel):
    id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class BaseResponseModel(BaseModel):
    """基础响应模型，用于统一API响应格式"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="操作消息")
    
    # Pydantic V2 风格
    model_config = {
        "from_attributes": True
    }

    