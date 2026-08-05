"""Create RBAC schema and seed MySQL defaults

Revision ID: 20260731_0001
Revises: 58c19980d43f
Create Date: 2026-07-31 00:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "20260731_0001"
down_revision: Union[str, Sequence[str], None] = "58c19980d43f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_USER = "-1"
ADMIN_PASSWORD_HASH = "$2b$12$F1nTxUIU9tsiA32SF3Pz1Okp9TBrLNa20zxXVI6KNja47M01M0Jea"


PERMISSIONS = [
    ("用户管理", "USER_MANAGE"),
    ("角色管理", "ROLE_MANAGE"),
    ("权限管理", "PERMISSION_MANAGE"),
    ("菜单管理", "MENU_MANAGE"),
    ("API限流管理", "RATE_LIMIT_MANAGE"),
    ("系统设置", "SYSTEM_SETTING"),
]


MENUS = [
    ("用户管理", "USER", "/system/user", 1),
    ("角色管理", "ROLE", "/system/role", 2),
    ("权限管理", "PERMISSION", "/system/permission", 3),
    ("菜单管理", "MENU", "/system/menu", 4),
    ("API限流管理", "API_RATE_LIMIT", "/system/api-rate-limit", 5),
    ("API文档", "API_DOCS", "/system/swagger-ui", 6),
]


API_PERMISSIONS = [
    ("GET", "/users/", "USER_MANAGE", "获取用户列表"),
    ("POST", "/users/admin/create", "USER_MANAGE", "管理员创建用户"),
    ("GET", "/users/list", "USER_MANAGE", "获取用户列表"),
    ("GET", "/users/detail/{user_id}", "USER_MANAGE", "获取用户详情"),
    ("PUT", "/users/update/{user_id}", "USER_MANAGE", "更新用户信息"),
    ("DELETE", "/users/delete/{user_id}", "USER_MANAGE", "删除用户"),
    ("POST", "/users/reset-password/{user_id}", "USER_MANAGE", "重置用户密码"),
    ("POST", "/users/assign-roles/{user_id}", "USER_MANAGE", "分配用户角色"),
    ("POST", "/users/remove-roles/{user_id}", "USER_MANAGE", "删除用户角色"),
    ("POST", "/roles", "ROLE_MANAGE", "创建角色"),
    ("GET", "/roles", "ROLE_MANAGE", "获取角色列表"),
    ("GET", "/roles/{role_id}", "ROLE_MANAGE", "获取角色详情"),
    ("PUT", "/roles/{role_id}", "ROLE_MANAGE", "更新角色"),
    ("DELETE", "/roles/{role_id}", "ROLE_MANAGE", "删除角色"),
    ("POST", "/roles/{role_id}/permissions", "ROLE_MANAGE", "为角色分配权限"),
    ("DELETE", "/roles/{role_id}/permissions", "ROLE_MANAGE", "移除角色的权限"),
    ("POST", "/roles/{role_id}/menus", "ROLE_MANAGE", "为角色分配菜单"),
    ("DELETE", "/roles/{role_id}/menus", "ROLE_MANAGE", "移除角色的菜单"),
    ("POST", "/permissions", "PERMISSION_MANAGE", "创建权限"),
    ("GET", "/permissions", "PERMISSION_MANAGE", "获取权限列表"),
    ("GET", "/permissions/api-bindings", "PERMISSION_MANAGE", "获取API权限绑定列表"),
    ("POST", "/permissions/api-bindings", "PERMISSION_MANAGE", "创建API权限绑定"),
    ("PUT", "/permissions/api-bindings/{api_permission_id}", "PERMISSION_MANAGE", "更新API权限绑定"),
    ("DELETE", "/permissions/api-bindings/{api_permission_id}", "PERMISSION_MANAGE", "删除API权限绑定"),
    ("GET", "/permissions/role/{role_id}", "PERMISSION_MANAGE", "获取角色拥有的权限"),
    ("GET", "/permissions/{permission_id}", "PERMISSION_MANAGE", "获取权限详情"),
    ("PUT", "/permissions/{permission_id}", "PERMISSION_MANAGE", "更新权限"),
    ("DELETE", "/permissions/{permission_id}", "PERMISSION_MANAGE", "删除权限"),
    ("POST", "/menus", "MENU_MANAGE", "创建菜单"),
    ("GET", "/menus", "MENU_MANAGE", "获取菜单列表"),
    ("GET", "/menus/tree", "MENU_MANAGE", "获取菜单树"),
    ("GET", "/menus/role/{role_id}", "MENU_MANAGE", "获取角色拥有的菜单"),
    ("GET", "/menus/{menu_id}", "MENU_MANAGE", "获取菜单详情"),
    ("PUT", "/menus/{menu_id}", "MENU_MANAGE", "更新菜单"),
    ("DELETE", "/menus/{menu_id}", "MENU_MANAGE", "删除菜单"),
    ("GET", "/rate-limit/stats", "RATE_LIMIT_MANAGE", "获取限流统计信息"),
    ("POST", "/rate-limit/whitelist", "RATE_LIMIT_MANAGE", "添加到白名单"),
    ("DELETE", "/rate-limit/whitelist/{identifier}", "RATE_LIMIT_MANAGE", "从白名单移除"),
    ("GET", "/rate-limit/whitelist", "RATE_LIMIT_MANAGE", "获取白名单列表"),
    ("POST", "/rate-limit/blacklist", "RATE_LIMIT_MANAGE", "添加到黑名单"),
    ("DELETE", "/rate-limit/blacklist/{identifier}", "RATE_LIMIT_MANAGE", "从黑名单移除"),
    ("GET", "/rate-limit/blacklist", "RATE_LIMIT_MANAGE", "获取黑名单列表"),
    ("POST", "/rate-limit/check", "RATE_LIMIT_MANAGE", "检查限流状态"),
    ("GET", "/rate-limit/config", "RATE_LIMIT_MANAGE", "获取限流配置"),
    ("PUT", "/rate-limit/config", "RATE_LIMIT_MANAGE", "更新限流配置"),
]


def audit_columns() -> list[sa.Column]:
    return [
        sa.Column("creation_date", sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.Column("created_by", sa.String(length=50), nullable=False, comment="创建人"),
        sa.Column("last_update_date", sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="修改时间"),
        sa.Column("last_updated_by", sa.String(length=50), nullable=False, comment="修改人"),
        sa.Column("last_update_login", sa.String(length=50), nullable=False, comment="最后登录ID"),
        sa.Column("delete_flag", sa.String(length=1), nullable=False, server_default="N", comment="删除标识，Y/N"),
        sa.Column("version_num", sa.Integer(), nullable=False, server_default="1", comment="版本号"),
    ]


def create_base_table(table_name: str, *columns: sa.Column, comment: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="主键ID"),
        *columns,
        *audit_columns(),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        comment=comment,
    )


def seed_defaults() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()

    sys_roles = sa.Table("sys_roles", metadata, autoload_with=bind)
    sys_permissions = sa.Table("sys_permissions", metadata, autoload_with=bind)
    sys_menus = sa.Table("sys_menus", metadata, autoload_with=bind)
    sys_users = sa.Table("sys_users", metadata, autoload_with=bind)
    sys_user_roles = sa.Table("sys_user_roles", metadata, autoload_with=bind)
    sys_role_permissions = sa.Table("sys_role_permissions", metadata, autoload_with=bind)
    sys_role_menus = sa.Table("sys_role_menus", metadata, autoload_with=bind)
    sys_api_permissions = sa.Table("sys_api_permissions", metadata, autoload_with=bind)

    now = datetime.now()
    audit = {
        "created_by": ADMIN_USER,
        "last_updated_by": ADMIN_USER,
        "last_update_login": ADMIN_USER,
        "delete_flag": "N",
        "version_num": 1,
    }

    bind.execute(sys_roles.insert(), [
        {
            "role_name": "超级管理员",
            "role_code": "ROLE_SUPER_ADMIN",
            "creation_date": now,
            "last_update_date": now,
            **audit,
        },
        {
            "role_name": "普通用户",
            "role_code": "ROLE_USER",
            "creation_date": now,
            "last_update_date": now,
            **audit,
        },
    ])

    bind.execute(sys_permissions.insert(), [
        {
            "permission_name": permission_name,
            "permission_code": permission_code,
            "creation_date": now,
            "last_update_date": now,
            **audit,
        }
        for permission_name, permission_code in PERMISSIONS
    ])

    bind.execute(sys_api_permissions.insert(), [
        {
            "method": method,
            "path_pattern": path_pattern,
            "permission_code": permission_code,
            "description": description,
            "enabled": 1,
            "creation_date": now,
            "last_update_date": now,
            **audit,
        }
        for method, path_pattern, permission_code, description in API_PERMISSIONS
    ])

    bind.execute(sys_menus.insert().values(
        menu_name="系统管理",
        menu_code="SYSTEM",
        menu_path="/system",
        parent_id=None,
        sort_order=1,
        creation_date=now,
        last_update_date=now,
        **audit,
    ))
    system_menu_id = bind.execute(
        sa.select(sys_menus.c.id).where(sys_menus.c.menu_code == "SYSTEM")
    ).scalar_one()

    bind.execute(sys_menus.insert(), [
        {
            "menu_name": menu_name,
            "menu_code": menu_code,
            "menu_path": menu_path,
            "parent_id": system_menu_id,
            "sort_order": sort_order,
            "creation_date": now,
            "last_update_date": now,
            **audit,
        }
        for menu_name, menu_code, menu_path, sort_order in MENUS
    ])

    bind.execute(sys_users.insert().values(
        user_name="admin",
        password=ADMIN_PASSWORD_HASH,
        phone_number="18888888888",
        email="admin@example.com",
        creation_date=now,
        last_update_date=now,
        **audit,
    ))

    admin_id = bind.execute(
        sa.select(sys_users.c.id).where(sys_users.c.user_name == "admin")
    ).scalar_one()
    role_id = bind.execute(
        sa.select(sys_roles.c.id).where(sys_roles.c.role_code == "ROLE_SUPER_ADMIN")
    ).scalar_one()

    bind.execute(sys_user_roles.insert().values(
        user_id=admin_id,
        role_id=role_id,
        creation_date=now,
        last_update_date=now,
        **audit,
    ))

    permission_ids = bind.execute(sa.select(sys_permissions.c.id)).scalars().all()
    bind.execute(sys_role_permissions.insert(), [
        {
            "role_id": role_id,
            "permission_id": permission_id,
            "creation_date": now,
            "last_update_date": now,
            **audit,
        }
        for permission_id in permission_ids
    ])

    menu_ids = bind.execute(sa.select(sys_menus.c.id)).scalars().all()
    bind.execute(sys_role_menus.insert(), [
        {
            "role_id": role_id,
            "menu_id": menu_id,
            "creation_date": now,
            "last_update_date": now,
            **audit,
        }
        for menu_id in menu_ids
    ])


def upgrade() -> None:
    """Upgrade schema."""
    create_base_table(
        "sys_users",
        sa.Column("user_name", sa.String(length=50), nullable=False, comment="用户名"),
        sa.Column("password", sa.String(length=100), nullable=False, comment="密码"),
        sa.Column("phone_number", sa.String(length=20), nullable=True, comment="手机号"),
        sa.Column("email", sa.String(length=100), nullable=True, comment="邮箱"),
        sa.UniqueConstraint("user_name", name="uk_user_name"),
        comment="用户信息表",
    )
    create_base_table(
        "sys_roles",
        sa.Column("role_name", sa.String(length=50), nullable=False, comment="角色名称"),
        sa.Column("role_code", sa.String(length=50), nullable=False, comment="角色编码"),
        sa.UniqueConstraint("role_code", name="uk_role_code"),
        comment="角色信息表",
    )
    create_base_table(
        "sys_permissions",
        sa.Column("permission_name", sa.String(length=50), nullable=False, comment="权限名称"),
        sa.Column("permission_code", sa.String(length=50), nullable=False, comment="权限编码"),
        sa.UniqueConstraint("permission_code", name="uk_permission_code"),
        comment="权限信息表",
    )
    create_base_table(
        "sys_api_permissions",
        sa.Column("method", sa.String(length=10), nullable=False, comment="HTTP方法"),
        sa.Column("path_pattern", sa.String(length=255), nullable=False, comment="API路径模式"),
        sa.Column("permission_code", sa.String(length=50), nullable=False, comment="权限编码"),
        sa.Column("description", sa.String(length=200), nullable=True, comment="说明"),
        sa.Column("enabled", mysql.TINYINT(display_width=1), nullable=False, server_default="1", comment="是否启用"),
        sa.UniqueConstraint("method", "path_pattern", name="uk_api_permission_route"),
        comment="API权限绑定表",
    )
    op.create_index("idx_api_permission_code", "sys_api_permissions", ["permission_code"])
    create_base_table(
        "sys_menus",
        sa.Column("menu_name", sa.String(length=50), nullable=False, comment="菜单名称"),
        sa.Column("menu_code", sa.String(length=50), nullable=False, comment="菜单编码"),
        sa.Column("menu_path", sa.String(length=200), nullable=True, comment="菜单路径"),
        sa.Column("parent_id", sa.BigInteger(), nullable=True, comment="父菜单ID"),
        sa.Column("sort_order", sa.Integer(), nullable=True, server_default="0", comment="显示顺序"),
        sa.UniqueConstraint("menu_code", name="uk_menu_code"),
        comment="菜单信息表",
    )
    create_base_table(
        "sys_user_roles",
        sa.Column("user_id", sa.BigInteger(), nullable=False, comment="用户ID"),
        sa.Column("role_id", sa.BigInteger(), nullable=False, comment="角色ID"),
        sa.ForeignKeyConstraint(["user_id"], ["sys_users.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["sys_roles.id"]),
        sa.UniqueConstraint("user_id", "role_id", name="uk_user_id_role_id"),
        comment="用户与角色关联表",
    )
    create_base_table(
        "sys_role_permissions",
        sa.Column("role_id", sa.BigInteger(), nullable=False, comment="角色ID"),
        sa.Column("permission_id", sa.BigInteger(), nullable=False, comment="权限ID"),
        sa.ForeignKeyConstraint(["role_id"], ["sys_roles.id"]),
        sa.ForeignKeyConstraint(["permission_id"], ["sys_permissions.id"]),
        sa.UniqueConstraint("role_id", "permission_id", name="uk_role_id_permission_id"),
        comment="角色与权限关联表",
    )
    create_base_table(
        "sys_role_menus",
        sa.Column("role_id", sa.BigInteger(), nullable=False, comment="角色ID"),
        sa.Column("menu_id", sa.BigInteger(), nullable=False, comment="菜单ID"),
        sa.ForeignKeyConstraint(["role_id"], ["sys_roles.id"]),
        sa.ForeignKeyConstraint(["menu_id"], ["sys_menus.id"]),
        sa.UniqueConstraint("role_id", "menu_id", name="uk_role_id_menu_id"),
        comment="角色与菜单关联表",
    )

    seed_defaults()


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sys_role_menus")
    op.drop_table("sys_role_permissions")
    op.drop_table("sys_user_roles")
    op.drop_table("sys_menus")
    op.drop_index("idx_api_permission_code", table_name="sys_api_permissions")
    op.drop_table("sys_api_permissions")
    op.drop_table("sys_permissions")
    op.drop_table("sys_roles")
    op.drop_table("sys_users")
