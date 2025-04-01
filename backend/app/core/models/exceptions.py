from fastapi import status


class AppException(Exception):
    """应用程序基础异常类
    
    所有自定义异常都应继承此类，提供统一的异常接口。
    
    Attributes:
        code: HTTP状态码
        message: 错误消息
        data: 额外的错误数据
    """
    def __init__(self, message: str, code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class BadRequestException(AppException):
    """客户端错误异常，表示请求参数错误或格式不正确"""
    def __init__(self, message: str = "请求参数错误", data=None):
        super().__init__(message=message, code=status.HTTP_400_BAD_REQUEST, data=data)


class UnauthorizedException(AppException):
    """未授权异常，表示用户未通过身份验证"""
    def __init__(self, message: str = "未授权访问", data=None):
        super().__init__(message=message, code=status.HTTP_401_UNAUTHORIZED, data=data)


class ForbiddenException(AppException):
    """禁止访问异常，表示用户没有权限执行请求的操作"""
    def __init__(self, message: str = "禁止访问该资源", data=None):
        super().__init__(message=message, code=status.HTTP_403_FORBIDDEN, data=data)


class NotFoundException(AppException):
    """资源不存在异常"""
    def __init__(self, message: str = "请求的资源不存在", data=None):
        super().__init__(message=message, code=status.HTTP_404_NOT_FOUND, data=data)


class ResourceConflictException(AppException):
    """资源冲突异常，例如创建已存在的资源"""
    def __init__(self, message: str = "资源冲突", data=None):
        super().__init__(message=message, code=status.HTTP_409_CONFLICT, data=data)


class ValidationException(AppException):
    """数据验证异常，表示数据不符合验证规则"""
    def __init__(self, message: str = "数据验证失败", data=None):
        super().__init__(message=message, code=status.HTTP_422_UNPROCESSABLE_ENTITY, data=data)


class DatabaseException(AppException):
    """数据库操作异常"""
    def __init__(self, message: str = "数据库操作失败", data=None):
        super().__init__(message=message, code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)


class ServiceException(AppException):
    """服务层异常，用于表示服务内部错误"""
    def __init__(self, message: str = "服务处理失败", data=None):
        super().__init__(message=message, code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)


class ExternalServiceException(AppException):
    """外部服务调用异常"""
    def __init__(self, message: str = "外部服务调用失败", data=None):
        super().__init__(message=message, code=status.HTTP_503_SERVICE_UNAVAILABLE, data=data)


class RateLimitException(AppException):
    """请求频率限制异常"""
    def __init__(self, message: str = "请求频率超出限制", data=None):
        super().__init__(message=message, code=status.HTTP_429_TOO_MANY_REQUESTS, data=data)
