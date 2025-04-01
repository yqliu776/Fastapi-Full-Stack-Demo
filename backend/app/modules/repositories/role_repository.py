from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models.rbac_model import SysRole
from app.modules.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[SysRole]):
    """
    角色仓储类，提供角色相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化角色仓储"""
        super().__init__(db_session, SysRole)
    
    async def get_by_code(self, role_code: str) -> Optional[SysRole]:
        """
        通过角色代码获取角色
        
        Args:
            role_code: 角色代码
            
        Returns:
            角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其权限信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含权限关联的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载权限关系
            await self.db.refresh(role, ["permissions"])
            
        return role
    
    async def get_role_with_menus(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其菜单信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含菜单关联的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载菜单关系
            await self.db.refresh(role, ["menus"])
            
        return role
    
    async def get_role_with_relations(self, role_id: int) -> Optional[SysRole]:
        """
        获取角色及其所有关联数据（用户、权限、菜单）
        
        Args:
            role_id: 角色ID
            
        Returns:
            包含所有关联数据的角色模型实例或None
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if role:
            # 加载所有关系
            await self.db.refresh(role, ["users", "permissions", "menus"])
            
        return role
    
    async def check_role_code_exists(self, role_code: str) -> bool:
        """
        检查角色代码是否已存在
        
        Args:
            role_code: 角色代码
            
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysRole.id).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_roles_by_filter(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        role_name: Optional[str] = None,
        role_code: Optional[str] = None
    ) -> List[SysRole]:
        """
        根据过滤条件获取角色列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            role_name: 角色名称过滤条件
            role_code: 角色代码过滤条件
            
        Returns:
            角色模型实例列表
        """
        filters = []
        
        if role_name:
            filters.append(SysRole.role_name.like(f"%{role_name}%"))
            
        if role_code:
            filters.append(SysRole.role_code.like(f"%{role_code}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters)