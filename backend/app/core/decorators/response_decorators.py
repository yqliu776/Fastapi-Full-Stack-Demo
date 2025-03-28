from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

from fastapi import Response, status
from fastapi.responses import JSONResponse

from app.core.models import ResponseModel
from app.core.tools import logger

F = TypeVar('F', bound=Callable[..., Any])


def response_wrapper(
    message: Optional[str] = None,
    code: int = status.HTTP_200_OK
) -> Callable[[F], F]:
    """响应包装装饰器
    
    用于自动包装路由函数的返回值，使其符合统一的响应格式。
    
    Args:
        message: 自定义响应消息，如果为None则使用默认消息
        code: 自定义状态码，默认为200
        
    Returns:
        装饰器函数
    
    Example:
        ```python
        @app.get("/users")
        @response_wrapper(message="获取用户列表成功")
        async def get_users():
            users = await user_service.get_all()
            return users  # 自动包装为 {"code": 200, "message": "获取用户列表成功", "data": users, "timestamp": 1234567890}
        ```
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # 执行原始函数
                result = await func(*args, **kwargs) if callable(func) else func
                
                # 如果返回值已经是Response对象，则直接返回
                if isinstance(result, Response):
                    return result
                
                # 如果返回值已经是ResponseModel对象，则转换为JSONResponse
                if isinstance(result, ResponseModel):
                    return JSONResponse(
                        status_code=result.code,
                        content=result.model_dump()
                    )
                
                # 否则，包装为统一响应格式
                response_message = message or "操作成功"
                response_data = ResponseModel(
                    code=code,
                    message=response_message,
                    data=result
                )
                
                return JSONResponse(
                    status_code=code,
                    content=response_data.model_dump()
                )
            except Exception as e:
                # 记录异常
                logger.error(f"路由处理发生异常: {str(e)}")
                # 返回统一的错误响应
                error_response = ResponseModel(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"服务器内部错误: {str(e)}",
                    data=None
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=error_response.model_dump()
                )
        
        return cast(F, wrapper)
    
    return decorator


def success_response(data: Any = None, message: str = "操作成功") -> ResponseModel:
    """创建成功响应
    
    用于手动创建统一格式的成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        ResponseModel: 包含状态码、消息、数据和时间戳的响应对象
    """
    return ResponseModel(
        code=status.HTTP_200_OK,
        message=message,
        data=data
    )


def error_response(message: str = "操作失败", code: int = status.HTTP_400_BAD_REQUEST, data: Any = None) -> ResponseModel:
    """创建错误响应
    
    用于手动创建统一格式的错误响应
    
    Args:
        message: 错误消息
        code: HTTP状态码
        data: 附加错误数据
    
    Returns:
        ResponseModel: 包含状态码、错误消息、数据和时间戳的响应对象
    """
    return ResponseModel(
        code=code,
        message=message,
        data=data
    ) 