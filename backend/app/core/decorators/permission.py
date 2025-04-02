from functools import wraps
from typing import List, Callable, Optional

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from app.core.settings import settings
from app.modules.schemas.auth_schema import TokenData
from app.services import oauth2_scheme


def require_permissions(required_permissions: List[str]):
    """
    权限控制装饰器
    
    验证当前用户是否拥有所需的权限。
    
    Args:
        required_permissions: 所需权限代码列表，满足其中任一权限即可访问
        
    Example:
        ```python
        @router.get("/users")
        @require_permissions(["user:list"])
        async def get_users():
            # 只有拥有"user:list"权限的用户才能访问
            pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, token: str = Depends(oauth2_scheme), **kwargs):
            # 验证令牌并检查权限
            credentials_exception = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
            try:
                # 解析令牌
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id: Optional[int] = payload.get("user_id")
                if user_id is None:
                    raise credentials_exception
                    
                token_data = TokenData(
                    user_id=user_id,
                    user_name=payload.get("user_name", ""),
                    permissions=payload.get("permissions", [])
                )
                
                # 检查权限
                user_permissions = token_data.permissions or []
                has_permission = False
                
                for permission in required_permissions:
                    if permission in user_permissions:
                        has_permission = True
                        break
                
                if not has_permission:
                    raise credentials_exception
                    
            except JWTError:
                raise credentials_exception
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def is_super_admin(token_data: TokenData) -> bool:
    """
    检查用户是否为超级管理员
    
    Args:
        token_data: 令牌数据
        
    Returns:
        bool: 是超级管理员返回True，否则返回False
    """
    # 可以根据实际需求定义超级管理员的判断条件
    # 例如：特定的角色码或权限码
    return "admin:all" in (token_data.permissions or []) 