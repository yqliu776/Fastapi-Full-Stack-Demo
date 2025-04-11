"""
Repository模块负责所有与数据库相关的操作
提供统一的数据访问接口，隔离数据库访问细节
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .permission_repository import PermissionRepository
from .role_repository import RoleRepository
from .menu_repository import MenuRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
    "MenuRepository"
] 