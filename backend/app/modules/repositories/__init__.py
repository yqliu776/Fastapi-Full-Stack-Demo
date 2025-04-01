"""
Repository模块负责所有与数据库相关的操作
提供统一的数据访问接口，隔离数据库访问细节
"""

from app.modules.repositories.base_repository import BaseRepository
from app.modules.repositories.user_repository import UserRepository
from app.modules.repositories.role_repository import RoleRepository
from app.modules.repositories.permission_repository import PermissionRepository
from app.modules.repositories.menu_repository import MenuRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
    "MenuRepository"
] 