from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.models import SysApiPermission
from .base_repository import BaseRepository


class ApiPermissionRepository(BaseRepository[SysApiPermission]):
    """API权限绑定仓储"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, SysApiPermission)

    async def get_by_route(
        self,
        method: str,
        path_pattern: str,
        enabled_only: bool = True
    ) -> Optional[SysApiPermission]:
        filters = [
            SysApiPermission.method == method.upper(),
            SysApiPermission.path_pattern == path_pattern,
            SysApiPermission.delete_flag == 'N'
        ]
        if enabled_only:
            filters.append(SysApiPermission.enabled == 1)

        query = select(SysApiPermission).where(
            and_(*filters)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_api_permissions_by_filter(
        self,
        skip: int = 0,
        limit: int = 100,
        method: Optional[str] = None,
        path_pattern: Optional[str] = None,
        permission_code: Optional[str] = None
    ) -> List[SysApiPermission]:
        filters = []

        if method:
            filters.append(SysApiPermission.method == method.upper())
        if path_pattern:
            filters.append(SysApiPermission.path_pattern.like(f"%{path_pattern}%"))
        if permission_code:
            filters.append(SysApiPermission.permission_code.like(f"%{permission_code}%"))

        return await self.get_multi(skip=skip, limit=limit, filters=filters)
