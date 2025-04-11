from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join
from typing import Optional, Tuple
from jose import jwt, JWTError
from datetime import timedelta

from app.modules.repositories import UserRepository, PermissionRepository, RoleRepository
from app.core.utils import verify_password, create_access_token, create_refresh_token
from app.modules.models import SysUser, SysPermission, SysRolePermission
from app.modules.schemas import TokenResponse, LoginRequest, TokenData
from .session_service import session_service
from app.core.connects.database import db
from app.core.settings import settings
from app.core.utils import RedisUtil


class AuthService:
    """认证服务类"""
    
    def __init__(self, db_session: AsyncSession = Depends(db.get_db)):
        self.db = db_session
        self.user_repository = UserRepository(db_session)
        self.role_repository = RoleRepository(db_session)
        self.permission_repository = PermissionRepository(db_session)
        self.redis_util = RedisUtil()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[SysUser]:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[SysUser]: 验证成功返回用户对象，失败返回None
        """
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """
        用户登录
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            TokenResponse: 包含访问令牌的响应
            
        Raises:
            HTTPException: 登录失败时抛出异常
        """
        user = await self.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户权限
        user_with_roles = await self.user_repository.get_user_with_roles(user.id)
        
        # 构建权限列表
        permissions = []
        for role in user_with_roles.roles:
            role_permissions = await self._get_role_permissions(role.id)
            permissions.extend([p.permission_code for p in role_permissions])
        
        # 创建令牌数据
        token_data = {
            "user_id": user.id,
            "user_name": user.user_name,
            "permissions": list(set(permissions))  # 去重
        }
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # 创建用户会话
        user_data = {
            "user_id": user.id,
            "username": user.user_name,
            "permissions": token_data["permissions"],
            "roles": [role.role_code for role in user_with_roles.roles]
        }
        session_id = await session_service.create_session(
            user.id,
            user_data,
            expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
            session_id=session_id  # 添加会话ID到响应中
        )
    
    async def _get_role_permissions(self, role_id: int):
        """
        获取角色的权限列表，使用Redis缓存优化
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限列表
        """
        # 构建缓存键
        cache_key = f"role_permissions:{role_id}"
        
        # 尝试从缓存获取
        cached_permission_codes = await self.redis_util.get(cache_key)
        if cached_permission_codes is not None:
            # 从缓存中获取权限代码，需要转换为权限对象
            query = select(SysPermission).where(SysPermission.permission_code.in_(cached_permission_codes))
            result = await self.db.execute(query)
            return result.scalars().all()
            
        # 缓存未命中，从数据库查询
        query = select(SysPermission).select_from(
            join(
                SysPermission,
                SysRolePermission,
                SysPermission.id == SysRolePermission.permission_id
            )
        ).where(SysRolePermission.role_id == role_id)
        
        result = await self.db.execute(query)
        permissions = result.scalars().all()
        
        # 只缓存权限代码
        permission_codes = [p.permission_code for p in permissions]
        
        # 将结果存入缓存，设置过期时间为1小时
        await self.redis_util.set(cache_key, permission_codes, ex=3600)
        
        return permissions
    
    async def _invalidate_role_permissions_cache(self, role_id: int):
        """
        使角色权限缓存失效
        
        Args:
            role_id: 角色ID
        """
        cache_key = f"role_permissions:{role_id}"
        await self.redis_util.delete(cache_key)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            TokenResponse: 新的访问令牌
            
        Raises:
            HTTPException: 刷新令牌无效或过期时抛出异常
        """
        try:
            # 验证刷新令牌
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 获取用户信息
            user = await self.user_repository.get_user_with_roles(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 创建新的令牌
            permissions = []
            for role in user.roles:
                # 使用专门的方法获取角色权限
                role_permissions = await self._get_role_permissions(role.id)
                permissions.extend([p.permission_code for p in role_permissions])
            
            token_data = {
                "user_id": user.id,
                "user_name": user.user_name,
                "permissions": list(set(permissions))
            }
            
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            new_refresh_token = create_refresh_token(
                data=token_data,
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            ) 