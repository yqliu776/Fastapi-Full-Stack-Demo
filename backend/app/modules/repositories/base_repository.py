from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select, update, delete, func, BinaryExpression, and_
from sqlalchemy.sql.expression import ColumnElement as SQLAColumnElement
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models.base_model import BaseModel

# 定义泛型类型T为BaseModel的子类
T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    基础仓储类，提供基本的CRUD操作
    """
    
    def __init__(self, db_session: AsyncSession, model_class: Type[T]):
        """
        初始化仓储
        
        Args:
            db_session: 数据库会话
            model_class: 模型类
        """
        self.db = db_session
        self.model_class = model_class
    
    async def create(self, obj_in: Union[Dict[str, Any], BaseModel]) -> T:
        """
        创建记录
        
        Args:
            obj_in: 创建对象的数据，可以是字典或Pydantic模型
        
        Returns:
            创建的数据库模型实例
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(
                exclude_unset=True,
                exclude={"id"}
            )
            
        db_obj = self.model_class(**create_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get(self, id_: Any) -> Optional[T]:
        """
        通过ID获取记录
        
        Args:
            id_: 记录ID
        
        Returns:
            数据库模型实例或None
        """
        query = select(self.model_class).where(
            and_(
                self.model_class.id == id_,
                self.model_class.delete_flag == "N"
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[List[Union[SQLAColumnElement, BinaryExpression, BooleanClauseList]]] = None,
        deleted: Optional[bool] = False
    ) -> List[T]:
        """
        获取多条记录
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            filters: 过滤条件列表
            deleted: 删除状态过滤，False仅正常(N)，True仅已删除(Y)，None不过滤
        
        Returns:
            数据库模型实例列表
        """
        query = select(self.model_class)
        if deleted is True:
            query = query.where(self.model_class.delete_flag == "Y")
        elif deleted is False:
            query = query.where(self.model_class.delete_flag == "N")
        
        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)
                
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        # 显式转换为List[T]类型
        return list(result.scalars().all())
    
    async def get_count(self, filters: Optional[List[Union[SQLAColumnElement, BinaryExpression, BooleanClauseList]]] = None, deleted: Optional[bool] = False) -> int:
        """
        获取符合条件的记录总数
        
        Args:
            filters: 过滤条件列表
            deleted: 删除状态过滤，False仅正常(N)，True仅已删除(Y)，None不过滤
        
        Returns:
            记录总数
        """
        query = select(func.count(self.model_class.id))
        if deleted is True:
            query = query.where(self.model_class.delete_flag == "Y")
        elif deleted is False:
            query = query.where(self.model_class.delete_flag == "N")
        
        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)
                
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def update(
        self, 
        *, 
        id_: Any, 
        obj_in: Union[Dict[str, Any], BaseModel]
    ) -> Optional[T]:
        """
        更新记录
        
        Args:
            id_: 记录ID
            obj_in: 更新数据，可以是字典或Pydantic模型
        
        Returns:
            更新后的数据库模型实例或None
        """
        db_obj = await self.get(id_)
        if not db_obj:
            return None
            
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        if "id" in update_data:
            del update_data["id"]

        query = update(self.model_class).where(
            and_(
                self.model_class.id == id_,
                self.model_class.delete_flag == "N"
            )
        ).values(**update_data)
        
        await self.db.execute(query)
        await self.db.commit()

        return await self.get(id_)
    
    async def delete(self, *, id_: Any) -> Optional[T]:
        """
        软删除记录（将delete_flag设置为Y）
        
        Args:
            id_: 记录ID
        
        Returns:
            删除的数据库模型实例或None
        """
        obj = await self.get(id_)
        if not obj:
            return None

        query = update(self.model_class).where(
            and_(
                self.model_class.id == id_,
                self.model_class.delete_flag == "N"
            )
        ).values(delete_flag="Y")
        
        await self.db.execute(query)
        await self.db.commit()

        return obj
    
    async def restore(self, *, id_: Any) -> Optional[T]:
        """
        恢复软删除记录（将delete_flag设置为N）
        
        Args:
            id_: 记录ID
            
        Returns:
            恢复后的数据库模型实例或None
        """
        query = update(self.model_class).where(
            and_(
                self.model_class.id == id_,
                self.model_class.delete_flag == "Y"
            )
        ).values(delete_flag="N")
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        if result.rowcount == 0:
            return None
        
        fetch = select(self.model_class).where(self.model_class.id == id_)
        obj = (await self.db.execute(fetch)).scalar_one_or_none()
        return obj

    async def purge(self, *, id_: Any) -> Optional[T]:
        """
        彻底删除记录（从数据库中物理删除，包括软删除的记录）
        
        Args:
            id_: 记录ID
        
        Returns:
            删除的数据库模型实例或None
        """
        fetch = select(self.model_class).where(
            self.model_class.id == id_
        )
        obj = (await self.db.execute(fetch)).scalar_one_or_none()
        if not obj:
            return None
            
        # 执行删除操作，不使用RETURNING子句
        query = delete(self.model_class).where(
            self.model_class.id == id_
        )
        
        await self.db.execute(query)
        await self.db.commit()
        
        # 返回之前查询的对象
        return obj 