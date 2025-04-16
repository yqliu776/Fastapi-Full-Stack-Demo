from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from typing import Optional, List, Tuple
import random
import string

from app.modules.schemas import UserCreate, UserUpdate, UserAdminCreate
from app.modules.models import SysUser, SysRole, SysUserRole
from app.core.utils import get_password_hash
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
        filters = [SysUser.delete_flag == 'N']
        
        if username:
            filters.append(SysUser.user_name.like(f"%{username}%"))
            
        if email:
            filters.append(SysUser.email.like(f"%{email}%"))
            
        if phone:
            filters.append(SysUser.phone_number.like(f"%{phone}%"))
            
        return await self.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def count_users_by_filter(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> int:
        """
        根据过滤条件获取用户总数
        
        Args:
            username: 用户名过滤条件
            email: 邮箱过滤条件
            phone: 手机号过滤条件
            
        Returns:
            符合条件的用户总数
        """
        filters = [SysUser.delete_flag == 'N']
        
        if username:
            filters.append(SysUser.user_name.like(f"%{username}%"))
            
        if email:
            filters.append(SysUser.email.like(f"%{email}%"))
            
        if phone:
            filters.append(SysUser.phone_number.like(f"%{phone}%"))
        
        query = select(func.count(SysUser.id)).where(and_(*filters))
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create_user_with_role(
        self,
        user_data: UserCreate,
        role_code: str,
        created_by: str
    ) -> SysUser:
        """
        创建用户并分配单个角色
        
        Args:
            user_data: 用户创建数据
            role_code: 角色代码
            created_by: 创建人
            
        Returns:
            创建的用户实例
        """
        # 获取角色ID
        role_query = select(SysRole.id).where(
            and_(
                SysRole.role_code == role_code,
                SysRole.delete_flag == 'N'
            )
        )
        role_result = await self.db.execute(role_query)
        role_id = role_result.scalar_one_or_none()
        
        if not role_id:
            # 如果角色不存在，创建一个默认用户角色
            new_role = SysRole(
                role_name="普通用户",
                role_code="user",
                created_by=created_by,
                last_updated_by=created_by,
                last_update_login=created_by
            )
            self.db.add(new_role)
            await self.db.flush()
            role_id = new_role.id
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = SysUser(
            user_name=user_data.user_name,
            password=hashed_password,
            email=user_data.email,
            phone_number=user_data.phone_number,
            created_by=created_by,
            last_updated_by=created_by,
            last_update_login=created_by
        )
        self.db.add(user)
        await self.db.flush()
        
        # 创建用户-角色关联
        user_role = SysUserRole(
            user_id=user.id,
            role_id=role_id,
            created_by=created_by,
            last_updated_by=created_by,
            last_update_login=created_by
        )
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def create_user_with_roles(
        self,
        user_data: UserAdminCreate,
        role_codes: List[str],
        created_by: str
    ) -> SysUser:
        """
        创建用户并分配多个角色
        
        Args:
            user_data: 用户创建数据
            role_codes: 角色代码列表
            created_by: 创建人
            
        Returns:
            创建的用户实例
        """
        # 获取角色ID列表
        role_query = select(SysRole.id, SysRole.role_code).where(
            and_(
                SysRole.role_code.in_(role_codes),
                SysRole.delete_flag == 'N'
            )
        )
        role_result = await self.db.execute(role_query)
        roles = role_result.fetchall()
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = SysUser(
            user_name=user_data.user_name,
            password=hashed_password,
            email=user_data.email,
            phone_number=user_data.phone_number,
            created_by=created_by,
            last_updated_by=created_by,
            last_update_login=created_by
        )
        self.db.add(user)
        await self.db.flush()
        
        # 创建用户-角色关联
        for role_id, _ in roles:
            user_role = SysUserRole(
                user_id=user.id,
                role_id=role_id,
                created_by=created_by,
                last_updated_by=created_by,
                last_update_login=created_by
            )
            self.db.add(user_role)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user_with_roles(
        self,
        user_id: int,
        user_data: UserUpdate,
        updated_by: str
    ) -> SysUser:
        """
        更新用户信息和角色
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            updated_by: 更新人
            
        Returns:
            更新后的用户实例
        """
        # 获取用户
        user = await self.get(user_id)
        if not user:
            return None
        
        # 更新用户基本信息
        update_data = user_data.model_dump(exclude_unset=True, exclude={"role_codes", "password"})
        if update_data:
            update_data["last_updated_by"] = updated_by
            update_data["last_update_login"] = updated_by
            
            # 如果有密码更新
            if user_data.password:
                update_data["password"] = get_password_hash(user_data.password)
                
            await self.update(id_=user_id, obj_in=update_data)
        
        # 如果有角色更新
        if user_data.role_codes:
            # 查询角色ID
            role_query = select(SysRole.id).where(
                and_(
                    SysRole.role_code.in_(user_data.role_codes),
                    SysRole.delete_flag == 'N'
                )
            )
            role_result = await self.db.execute(role_query)
            role_ids = [row[0] for row in role_result.fetchall()]
            
            # 删除原有用户角色关联
            await self.db.execute(
                update(SysUserRole)
                .where(SysUserRole.user_id == user_id)
                .values(delete_flag="Y", last_updated_by=updated_by, last_update_login=updated_by)
            )
            
            # 创建新的用户角色关联
            for role_id in role_ids:
                user_role = SysUserRole(
                    user_id=user_id,
                    role_id=role_id,
                    created_by=updated_by,
                    last_updated_by=updated_by,
                    last_update_login=updated_by
                )
                self.db.add(user_role)
        
        await self.db.commit()
        return await self.get(user_id)
    
    async def reset_password(
        self,
        user_id: int,
        updated_by: str,
        password_length: int = 8
    ) -> Tuple[str, SysUser]:
        """
        重置用户密码
        
        Args:
            user_id: 用户ID
            updated_by: 更新人
            password_length: 新密码长度
            
        Returns:
            新密码和更新后的用户实例
        """
        # 生成随机密码
        chars = string.ascii_letters + string.digits
        new_password = ''.join(random.choice(chars) for _ in range(password_length))
        
        # 更新用户密码
        hashed_password = get_password_hash(new_password)
        update_data = {
            "password": hashed_password,
            "last_updated_by": updated_by,
            "last_update_login": updated_by
        }
        
        user = await self.update(id_=user_id, obj_in=update_data)
        
        return new_password, user 