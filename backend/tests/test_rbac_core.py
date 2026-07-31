import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_TYPE", "mysql")
os.environ.setdefault("MYSQL_SERVER", "localhost:3306")
os.environ.setdefault("MYSQL_USER", "root")
os.environ.setdefault("MYSQL_PASSWORD", "FastFullStack123")
os.environ.setdefault("MYSQL_DB", "fast_full_stack_demo_test")
os.environ.setdefault("REDIS_PASSWORD", "FastFullStackRedis123")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.connects.database import Base, db
from app.core.utils.redis_util import RedisUtil
from app.modules.models import (
    SysMenu,
    SysPermission,
    SysRole,
    SysRoleMenu,
    SysRolePermission,
    SysUser,
    SysUserRole,
)
from app.modules.repositories import MenuRepository, PermissionRepository, RoleRepository
from app.routers.auth import get_current_user
from app.routers.rbac.menu_router import router as menu_router


TEST_DB_NAME = os.environ["MYSQL_DB"]


def _mysql_admin_url() -> str:
    server = os.environ["MYSQL_SERVER"]
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    return f"mysql+pymysql://{user}:{password}@{server}/mysql?charset=utf8mb4"


def _mysql_async_url() -> str:
    server = os.environ["MYSQL_SERVER"]
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    return f"mysql+aiomysql://{user}:{password}@{server}/{TEST_DB_NAME}?charset=utf8mb4"


@pytest.fixture(scope="session")
def mysql_test_database():
    if TEST_DB_NAME != "fast_full_stack_demo_test":
        pytest.skip("RBAC tests only manage the dedicated fast_full_stack_demo_test database")

    admin_engine = create_engine(_mysql_admin_url(), pool_pre_ping=True)
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{TEST_DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            connection.commit()
    except Exception as exc:
        pytest.skip(f"MySQL test database is unavailable: {exc}")

    yield

    with admin_engine.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS `{TEST_DB_NAME}`"))
        connection.commit()
    admin_engine.dispose()


@pytest_asyncio.fixture
async def async_engine(mysql_test_database):
    engine = create_async_engine(_mysql_async_url(), pool_pre_ping=True)
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch):
    async def redis_get(cls, key):
        return None

    async def redis_set(cls, key, value, ex=None):
        return True

    async def redis_delete(cls, *keys):
        return 0

    monkeypatch.setattr(RedisUtil, "get", classmethod(redis_get))
    monkeypatch.setattr(RedisUtil, "set", classmethod(redis_set))
    monkeypatch.setattr(RedisUtil, "delete", classmethod(redis_delete))


@pytest_asyncio.fixture
async def session(async_engine):
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session
        await db_session.rollback()


def _audit(user: str = "pytest") -> dict:
    return {
        "created_by": user,
        "last_updated_by": user,
        "last_update_login": user,
    }


async def _create_role(session: AsyncSession, code: str = "ROLE_TEST") -> SysRole:
    role = SysRole(role_name=code, role_code=code, **_audit())
    session.add(role)
    await session.flush()
    return role


async def _create_permission(session: AsyncSession, code: str) -> SysPermission:
    permission = SysPermission(permission_name=code, permission_code=code, **_audit())
    session.add(permission)
    await session.flush()
    return permission


async def _create_menu(session: AsyncSession, code: str, path: str, parent_id: int | None = None) -> SysMenu:
    menu = SysMenu(
        menu_name=code,
        menu_code=code,
        menu_path=path,
        parent_id=parent_id,
        sort_order=0,
        **_audit(),
    )
    session.add(menu)
    await session.flush()
    return menu


@pytest.mark.asyncio
async def test_role_permission_assign_remove_and_reassign(session: AsyncSession):
    role = await _create_role(session)
    first = await _create_permission(session, "FIRST_PERMISSION")
    second = await _create_permission(session, "SECOND_PERMISSION")
    await session.commit()

    role_repository = RoleRepository(session)
    permission_repository = PermissionRepository(session)

    assert await role_repository.add_permissions_to_role(role.id, [first.id, second.id], _audit())
    permissions = await permission_repository.get_permissions_by_role_id(role.id)
    assert {permission.permission_code for permission in permissions} == {"FIRST_PERMISSION", "SECOND_PERMISSION"}

    assert await role_repository.remove_permissions_from_role(role.id, [first.id])
    permissions = await permission_repository.get_permissions_by_role_id(role.id)
    assert [permission.permission_code for permission in permissions] == ["SECOND_PERMISSION"]

    assert await role_repository.add_permissions_to_role(role.id, [first.id], _audit("pytest-reassign"))
    permissions = await permission_repository.get_permissions_by_role_id(role.id)
    assert {permission.permission_code for permission in permissions} == {"FIRST_PERMISSION", "SECOND_PERMISSION"}

    relation = await session.get(SysRolePermission, 1)
    assert relation is not None
    assert relation.delete_flag == "N"
    assert relation.last_updated_by == "pytest-reassign"


@pytest.mark.asyncio
async def test_soft_deleted_role_permission_is_not_returned(session: AsyncSession):
    role = await _create_role(session)
    active = await _create_permission(session, "ACTIVE_PERMISSION")
    removed = await _create_permission(session, "REMOVED_PERMISSION")
    session.add_all(
        [
            SysRolePermission(role_id=role.id, permission_id=active.id, delete_flag="N", **_audit()),
            SysRolePermission(role_id=role.id, permission_id=removed.id, delete_flag="Y", **_audit()),
        ]
    )
    await session.commit()

    permission_repository = PermissionRepository(session)
    menu_repository = MenuRepository(session)

    permissions = await permission_repository.get_permissions_by_role_id(role.id)
    assert [permission.permission_code for permission in permissions] == ["ACTIVE_PERMISSION"]

    parent = await _create_menu(session, "PARENT", "/system")
    visible = await _create_menu(session, "VISIBLE_MENU", "/system/visible", parent.id)
    hidden = await _create_menu(session, "HIDDEN_MENU", "/system/hidden", parent.id)
    user = SysUser(user_name="rbac_user", password="not-used", **_audit())
    session.add(user)
    await session.flush()
    session.add_all(
        [
            SysUserRole(user_id=user.id, role_id=role.id, delete_flag="N", **_audit()),
            SysRoleMenu(role_id=role.id, menu_id=parent.id, delete_flag="N", **_audit()),
            SysRoleMenu(role_id=role.id, menu_id=visible.id, delete_flag="N", **_audit()),
            SysRoleMenu(role_id=role.id, menu_id=hidden.id, delete_flag="Y", **_audit()),
        ]
    )
    await session.commit()

    menus = await menu_repository.get_menus_by_user_id(user.id)
    assert {menu.menu_code for menu in menus} == {"PARENT", "VISIBLE_MENU"}


@pytest.mark.asyncio
async def test_current_menus_only_returns_authenticated_user_menus(session: AsyncSession):
    first_role = await _create_role(session, "ROLE_FIRST")
    second_role = await _create_role(session, "ROLE_SECOND")
    first_menu = await _create_menu(session, "FIRST_MENU", "/system/first")
    second_menu = await _create_menu(session, "SECOND_MENU", "/system/second")
    first_user = SysUser(user_name="first_user", password="not-used", **_audit())
    second_user = SysUser(user_name="second_user", password="not-used", **_audit())
    session.add_all([first_user, second_user])
    await session.flush()
    session.add_all(
        [
            SysUserRole(user_id=first_user.id, role_id=first_role.id, **_audit()),
            SysUserRole(user_id=second_user.id, role_id=second_role.id, **_audit()),
            SysRoleMenu(role_id=first_role.id, menu_id=first_menu.id, **_audit()),
            SysRoleMenu(role_id=second_role.id, menu_id=second_menu.id, **_audit()),
        ]
    )
    await session.commit()

    async def override_get_db():
        yield session

    app = FastAPI()
    app.include_router(menu_router)
    app.dependency_overrides[db.get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=first_user.id, user_name=first_user.user_name)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/menus/current")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert {menu["menu_code"] for menu in payload["data"]["items"]} == {"FIRST_MENU"}
