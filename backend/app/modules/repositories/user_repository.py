from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from app.modules.models import SysUser, SysRole
from .base_repository import BaseRepository


class UserRepository(BaseRepository[SysUser]):
    """
    用户仓储类，提供用户相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化用户仓储"""
        super().__init__(db_session, SysUser)
    
    async def get_by_username(self, username: str) -> Optional[SysUser]:
        """
        通过用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户模型实例或None
        """
        query = select(SysUser).where(
            and_(
                SysUser.user_name == username,
                SysUser.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_with_roles(self, user_id: int) -> Optional[SysUser]:
        """
        获取用户及其角色信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含角色关联的用户模型实例或None
        """
        query = select(SysUser).where(
            and_(
                SysUser.id == user_id,
                SysUser.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            # 加载角色关系
            await self.db.refresh(user, ["roles"])
            
        return user
    
    async def get_users_by_role(self, role_code: str, skip: int = 0, limit: int = 100) -> List[SysUser]:
        """
        通过角色代码获取用户列表
        
        Args:
            role_code: 角色代码
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            用户模型实例列表
        """
        # 查询具有特定角色代码的角色
        role_query = select(SysRole).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag == 'N'
            )
        )
        role_result = await self.db.execute(role_query)
        role = role_result.scalar_one_or_none()
        
        if not role:
            return []
        
        # 加载该角色下的所有用户
        await self.db.refresh(role, ["users"])
        users = role.users
        
        # 应用分页逻辑
        start = min(skip, len(users))
        end = min(skip + limit, len(users))
        
        return users[start:end]
    
    async def check_username_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在
        
        Args:
            username: 用户名
            
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysUser.id).where(
            and_(
                SysUser.user_name == username,
                SysUser.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_users_by_filter(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> List[SysUser]:
        """
        根据过滤条件获取用户列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            username: 用户名过滤条件
            email: 邮箱过滤条件
            phone: 手机号过滤条件
            
        Returns:
            用户模型实例列表
        """
        filters = []
        
        if username:
            filters.append(SysUser.user_name.like(f"%{username}%"))
            
        if email:
            filters.append(SysUser.email.like(f"%{email}%"))
            
        if phone:
            filters.append(SysUser.phone_number.like(f"%{phone}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters) 