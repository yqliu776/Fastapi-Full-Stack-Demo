from fastapi import Depends, HTTPException, status
from typing import List, Optional, Callable
from functools import wraps
from jose import jwt

from app.core.settings import settings
from app.services import oauth2_scheme


def has_permission(required_permissions: List[str]):
    """
    权限验证装饰器，检查当前用户是否拥有所需权限
    
    Args:
        required_permissions: 所需的权限代码列表，用户必须拥有所有列出的权限
    
    Returns:
        依赖函数，用于FastAPI路由的权限验证
    """
    
    def permission_checker(token: str = Depends(oauth2_scheme)) -> bool:
        """
        检查用户权限
        
        Args:
            token: JWT令牌
            
        Returns:
            如果权限验证通过，返回True
            
        Raises:
            HTTPException: 权限验证失败时抛出异常
        """
        # 如果没有要求任何权限，直接通过
        if not required_permissions:
            return True
            
        try:
            # 解析令牌
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            permissions: Optional[List[str]] = payload.get("permissions")
            
            # 检查用户是否拥有超级管理员权限
            if "ROLE_SUPER_ADMIN" in permissions:
                return True
                
            # 检查用户是否拥有所需权限
            for permission in required_permissions:
                if permission not in permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您没有执行此操作的权限"
                    )
                    
            return True
            
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的身份凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    return permission_checker


def require_permission(*permissions: str) -> Callable:
    """
    权限验证装饰器，用于路由处理函数
    
    Args:
        permissions: 所需的权限代码，用户必须拥有所有列出的权限
    
    Returns:
        装饰器函数
    """
    
    def decorator(func: Callable) -> Callable:
        # 定义具有相同签名的包装函数
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前请求的token
            token = kwargs.get("token") if "token" in kwargs else None
            
            if not token:
                for arg in args:
                    # 尝试从位置参数中找到token
                    if isinstance(arg, str) and arg.startswith("eyJ"):
                        token = arg
                        break
                        
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未提供身份凭证",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # 解析token
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_permissions: Optional[List[str]] = payload.get("permissions", [])
                
                # 检查超级管理员权限
                if "ROLE_SUPER_ADMIN" in user_permissions:
                    return await func(*args, **kwargs)
                    
                # 检查具体权限
                for permission in permissions:
                    if permission not in user_permissions:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="您没有执行此操作的权限"
                        )
                        
                # 所有权限验证通过
                return await func(*args, **kwargs)
                
            except jwt.JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的身份凭证",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        return wrapper
        
    return decorator 