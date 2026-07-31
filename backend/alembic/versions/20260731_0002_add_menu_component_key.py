"""Add menu component key

Revision ID: 20260731_0002
Revises: 20260731_0001
Create Date: 2026-07-31 00:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = "20260731_0002"
down_revision: Union[str, Sequence[str], None] = "20260731_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MENU_COMPONENT_KEYS = {
    "SYSTEM": "dashboard",
    "USER": "user",
    "ROLE": "role",
    "PERMISSION": "permission",
    "MENU": "menu",
    "API_RATE_LIMIT": "rate_limit",
    "API_DOCS": "swagger",
}


def upgrade() -> None:
    op.add_column(
        "sys_menus",
        sa.Column("component_key", sa.String(length=100), nullable=True, comment="前端组件Key"),
    )

    for menu_code, component_key in MENU_COMPONENT_KEYS.items():
        op.execute(f"UPDATE sys_menus SET component_key = '{component_key}' WHERE menu_code = '{menu_code}'")

    bind = op.get_bind()
    now = datetime.now()
    api_permissions = sa.Table(
        "sys_api_permissions",
        sa.MetaData(),
        sa.Column("method", sa.String(length=10)),
        sa.Column("path_pattern", sa.String(length=255)),
        sa.Column("permission_code", sa.String(length=50)),
        sa.Column("description", sa.String(length=200)),
        sa.Column("enabled", sa.Integer()),
        sa.Column("creation_date", sa.DateTime()),
        sa.Column("created_by", sa.String(length=50)),
        sa.Column("last_update_date", sa.DateTime()),
        sa.Column("last_updated_by", sa.String(length=50)),
        sa.Column("last_update_login", sa.String(length=50)),
        sa.Column("delete_flag", sa.String(length=1)),
        sa.Column("version_num", sa.Integer()),
    )
    bind.execute(api_permissions.insert(), [
        {
            "method": "PUT",
            "path_pattern": "/roles/{role_id}/permissions",
            "permission_code": "ROLE_MANAGE",
            "description": "保存角色权限完整集合",
            "enabled": 1,
            "creation_date": now,
            "created_by": "-1",
            "last_update_date": now,
            "last_updated_by": "-1",
            "last_update_login": "-1",
            "delete_flag": "N",
            "version_num": 1,
        },
        {
            "method": "PUT",
            "path_pattern": "/roles/{role_id}/menus",
            "permission_code": "ROLE_MANAGE",
            "description": "保存角色菜单完整集合",
            "enabled": 1,
            "creation_date": now,
            "created_by": "-1",
            "last_update_date": now,
            "last_updated_by": "-1",
            "last_update_login": "-1",
            "delete_flag": "N",
            "version_num": 1,
        },
    ])


def downgrade() -> None:
    op.execute("DELETE FROM sys_api_permissions WHERE method = 'PUT' AND path_pattern IN ('/roles/{role_id}/permissions', '/roles/{role_id}/menus')")
    op.drop_column("sys_menus", "component_key")
