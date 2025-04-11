from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from app.modules.models import SysMenu, SysRoleMenu
from .base_repository import BaseRepository


class MenuRepository(BaseRepository[SysMenu]):
    """
    菜单仓储类，提供菜单相关的数据库操作
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化菜单仓储"""
        super().__init__(db_session, SysMenu)
    
    async def get_by_menu_code(self, menu_code: str) -> Optional[SysMenu]:
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
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_menu_with_roles(self, menu_id: int) -> Optional[SysMenu]:
        """
        获取菜单及其角色信息
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            包含角色关联的菜单模型实例或None
        """
        query = select(SysMenu).where(
            and_(
                SysMenu.id == menu_id,
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        menu = result.scalar_one_or_none()
        
        if menu:
            # 加载角色关系
            await self.db.refresh(menu, ["roles"])
            
        return menu
    
    async def get_menu_tree(self) -> List[SysMenu]:
        """
        获取所有菜单，按照树形结构排序
        
        Returns:
            菜单模型实例列表，顶级菜单在前
        """
        query = select(SysMenu).where(
            SysMenu.delete_flag == 'N'
        ).order_by(
            # MySQL不支持nulls_first()语法，使用CASE表达式来实现相同功能
            SysMenu.parent_id.is_(None).desc(),
            SysMenu.parent_id,
            SysMenu.sort_order
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_menus_by_parent_id(self, parent_id: Optional[int] = None) -> List[SysMenu]:
        """
        获取指定父菜单下的所有子菜单
        
        Args:
            parent_id: 父菜单ID，如果为None则获取所有顶级菜单
            
        Returns:
            菜单模型实例列表
        """
        if parent_id is None:
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id.is_(None),
                    SysMenu.delete_flag == 'N'
                )
            ).order_by(SysMenu.sort_order)
        else:
            query = select(SysMenu).where(
                and_(
                    SysMenu.parent_id == parent_id,
                    SysMenu.delete_flag == 'N'
                )
            ).order_by(SysMenu.sort_order)
            
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
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
                SysMenu.delete_flag == 'N'
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_menus_by_role_id(self, role_id: int) -> List[SysMenu]:
        """
        获取角色拥有的所有菜单
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单模型实例列表
        """
        from sqlalchemy import join
        
        # 使用JOIN查询角色的菜单
        query = select(SysMenu).select_from(
            join(
                SysMenu,
                SysRoleMenu,
                SysMenu.id == SysRoleMenu.menu_id
            )
        ).where(
            and_(
                SysRoleMenu.role_id == role_id,
                SysMenu.delete_flag == 'N'
            )
        ).order_by(
            # MySQL不支持nulls_first()语法，使用CASE表达式来实现相同功能
            # 如果parent_id为NULL, 则排在前面
            SysMenu.parent_id.is_(None).desc(),
            SysMenu.parent_id,
            SysMenu.sort_order
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())