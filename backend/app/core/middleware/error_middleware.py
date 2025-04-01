from typing import Callable, Dict, Any
import traceback
import json
from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.utils import logger
from app.core.models import ResponseModel
from app.core.models.exceptions import AppException


class ErrorHandlerMiddleware:
    """全局错误处理中间件
    
    用于捕获和处理应用中的各种异常，提供统一的错误响应格式。
    
    Attributes:
        app: FastAPI应用实例
    """
    
    def __init__(self, app: FastAPI):
        """初始化错误处理中间件。
        
        Args:
            app: FastAPI应用实例
        """
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> JSONResponse:
        """处理请求并捕获可能发生的异常。
        
        Args:
            request: FastAPI请求对象
            call_next: 处理下一个中间件的可调用对象
            
        Returns:
            JSONResponse: 标准格式的JSON响应
        """
        try:
            return await call_next(request)
        
        except AppException as e:
            # 处理自定义应用异常
            return self._handle_app_exception(e)
            
        except StarletteHTTPException as e:
            # 处理FastAPI/Starlette HTTP异常
            return self._handle_http_exception(e)
            
        except RequestValidationError as e:
            # 处理请求验证错误
            return self._handle_validation_exception(e)
            
        except ValidationError as e:
            # 处理Pydantic验证错误
            return self._handle_pydantic_validation(e)
            
        except SQLAlchemyError as e:
            # 处理数据库异常
            return self._handle_database_exception(e)
            
        except Exception as e:
            # 处理所有其他异常
            return self._handle_internal_exception(e, request)
    
    def _handle_app_exception(self, exc: AppException) -> JSONResponse:
        """处理自定义应用异常
        
        Args:
            exc: 应用异常实例
            
        Returns:
            JSONResponse: 包含错误详情的响应
        """
        response = ResponseModel(
            code=exc.code, 
            message=exc.message,
            data=exc.data
        )
        
        logger.warning(f"应用异常: {exc.message} (代码: {exc.code})")
        return JSONResponse(
            status_code=exc.code,
            content=response.model_dump()
        )
    
    def _handle_http_exception(self, exc: StarletteHTTPException) -> JSONResponse:
        """处理HTTP异常
        
        Args:
            exc: HTTP异常实例
            
        Returns:
            JSONResponse: 包含错误详情的响应
        """
        response = ResponseModel(
            code=exc.status_code,
            message=str(exc.detail),
            data=None
        )
        
        logger.warning(f"HTTP异常: {exc.detail} (状态码: {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump()
        )
    
    def _handle_validation_exception(self, exc: RequestValidationError) -> JSONResponse:
        """处理请求验证错误
        
        Args:
            exc: 请求验证错误实例
            
        Returns:
            JSONResponse: 包含验证错误详情的响应
        """
        # 格式化验证错误信息
        error_details = []
        for error in exc.errors():
            error_details.append({
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", "")
            })
        
        response = ResponseModel(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="请求数据验证失败",
            data=error_details
        )
        
        logger.warning(f"请求验证错误: {json.dumps(error_details, ensure_ascii=False)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump()
        )
    
    def _handle_pydantic_validation(self, exc: ValidationError) -> JSONResponse:
        """处理Pydantic验证错误
        
        Args:
            exc: Pydantic验证错误实例
            
        Returns:
            JSONResponse: 包含验证错误详情的响应
        """
        error_details = json.loads(exc.json())
        
        response = ResponseModel(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="数据模型验证失败",
            data=error_details
        )
        
        logger.warning(f"Pydantic验证错误: {json.dumps(error_details, ensure_ascii=False)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump()
        )
    
    def _handle_database_exception(self, exc: SQLAlchemyError) -> JSONResponse:
        """处理数据库异常
        
        Args:
            exc: SQLAlchemy异常实例
            
        Returns:
            JSONResponse: 包含数据库错误详情的响应
        """
        response = ResponseModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"数据库操作失败: {str(exc)}",
            data=None
        )
        
        logger.error(f"数据库异常: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump()
        )
    
    def _handle_internal_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """处理内部服务器异常
        
        Args:
            exc: 异常实例
            request: 请求对象
            
        Returns:
            JSONResponse: 包含错误详情的响应
        """
        # 获取完整的异常堆栈
        error_stack = traceback.format_exc()
        
        # 日志记录详细异常信息
        logger.error(
            f"内部服务器错误: {str(exc)}\n"
            f"路径: {request.url.path}\n"
            f"方法: {request.method}\n"
            f"异常堆栈: {error_stack}"
        )
        
        # 生产环境下不返回详细错误信息给客户端
        response = ResponseModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="服务器内部错误",
            data=None if not self.app.debug else {
                "error": str(exc),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump()
        ) 