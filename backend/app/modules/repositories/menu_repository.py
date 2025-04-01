from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models.rbac_model import SysMenu, SysRole
from app.modules.repositories.base_repository import BaseRepository


class MenuRepository(BaseRepository[SysMenu]):
    """
    菜单仓储类，提供菜单相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化菜单仓储"""
        super().__init__(db_session, SysMenu)
    
    async def get_by_code(self, menu_code: str) -> Optional[SysMenu]:
        """
        通过菜单代码获取菜单
        
        Args:
            menu_code: 菜单代码
            
        Returns:
            菜单模型实例或None
        """
        query = select(SysMenu).where(
            and_(
                SysMenu.menu_code == menu_code,
                SysMenu.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_menus_by_role(self, role_id: int) -> List[SysMenu]:
        """
        获取角色拥有的所有菜单
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单模型实例列表
        """
        query = select(SysRole).where(
            and_(
                SysRole.id == role_id,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            return []
        
        # 加载角色菜单关系
        await self.db.refresh(role, ["menus"])
        return role.menus
    
    async def get_menus_by_role_code(self, role_code: str) -> List[SysMenu]:
        """
        通过角色代码获取所有菜单
        
        Args:
            role_code: 角色代码
            
        Returns:
            菜单模型实例列表
        """
        query = select(SysRole).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            return []
        
        # 加载角色菜单关系
        await self.db.refresh(role, ["menus"])
        return role.menus
    
    async def get_submenus(self, parent_id: int) -> List[SysMenu]:
        """
        获取子菜单列表
        
        Args:
            parent_id: 父菜单ID
            
        Returns:
            子菜单模型实例列表
        """
        query = select(SysMenu).where(
            and_(
                SysMenu.parent_id == parent_id,
                SysMenu.delete_flag.is_("N")
            )
        ).order_by(SysMenu.sort_order)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_menu_tree(self, parent_id: Optional[int] = None) -> List[SysMenu]:
        """
        获取菜单树，递归查询子菜单
        
        Args:
            parent_id: 父菜单ID，默认为None表示获取顶级菜单
            
        Returns:
            菜单树列表
        """
        if parent_id is None:
            # 获取顶级菜单（parent_id为空的菜单）
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id.is_(None),
                    SysMenu.delete_flag.is_("N")
                )
            ).order_by(SysMenu.sort_order)
        else:
            # 获取指定父ID的子菜单
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id == parent_id,
                    SysMenu.delete_flag.is_("N")
                )
            ).order_by(SysMenu.sort_order)
        
        result = await self.db.execute(query)
        menus = list(result.scalars().all())
        
        # 递归获取每个菜单的子菜单
        for menu in menus:
            children = await self.get_menu_tree(menu.id)
            menu.children = children
            
        return menus
    
    async def check_menu_code_exists(self, menu_code: str) -> bool:
        """
        检查菜单代码是否已存在
        
        Args:
            menu_code: 菜单代码
            
        Returns:
            如果存在返回True，否则返回False
        """
        query = select(SysMenu.id).where(
            and_(
                SysMenu.menu_code == menu_code,
                SysMenu.delete_flag.is_("N")
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_menus_by_filter(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        menu_name: Optional[str] = None,
        menu_code: Optional[str] = None,
        menu_path: Optional[str] = None
    ) -> List[SysMenu]:
        """
        根据过滤条件获取菜单列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            menu_name: 菜单名称过滤条件
            menu_code: 菜单代码过滤条件
            menu_path: 菜单路径过滤条件
            
        Returns:
            菜单模型实例列表
        """
        filters = []
        
        if menu_name:
            filters.append(SysMenu.menu_name.like(f"%{menu_name}%"))
            
        if menu_code:
            filters.append(SysMenu.menu_code.like(f"%{menu_code}%"))
            
        if menu_path:
            filters.append(SysMenu.menu_path.like(f"%{menu_path}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters) 