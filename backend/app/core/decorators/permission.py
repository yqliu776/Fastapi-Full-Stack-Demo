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
            permissions: Optional[List[str]] = payload.get("permissions") or []
            if not permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限信息"
                )
            
            # 检查token类型，只允许access token
            token_type = payload.get("type")
            if token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
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