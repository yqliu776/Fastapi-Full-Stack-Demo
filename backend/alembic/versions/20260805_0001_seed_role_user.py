"""Seed default user role

Revision ID: 20260805_0001
Revises: 20260731_0002
Create Date: 2026-08-05 00:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = "20260805_0001"
down_revision: Union[str, Sequence[str], None] = "20260731_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _roles_table() -> sa.Table:
    return sa.Table(
        "sys_roles",
        sa.MetaData(),
        sa.Column("id", sa.BigInteger()),
        sa.Column("role_name", sa.String(length=50)),
        sa.Column("role_code", sa.String(length=50)),
        sa.Column("creation_date", sa.DateTime()),
        sa.Column("created_by", sa.String(length=50)),
        sa.Column("last_update_date", sa.DateTime()),
        sa.Column("last_updated_by", sa.String(length=50)),
        sa.Column("last_update_login", sa.String(length=50)),
        sa.Column("delete_flag", sa.String(length=1)),
        sa.Column("version_num", sa.Integer()),
    )


def upgrade() -> None:
    bind = op.get_bind()
    roles = _roles_table()

    exists = bind.execute(
        sa.select(roles.c.id).where(roles.c.role_code == "ROLE_USER")
    ).scalar_one_or_none()
    if exists:
        return

    now = datetime.now()
    bind.execute(roles.insert().values(
        role_name="普通用户",
        role_code="ROLE_USER",
        creation_date=now,
        created_by="-1",
        last_update_date=now,
        last_updated_by="-1",
        last_update_login="-1",
        delete_flag="N",
        version_num=1,
    ))


def downgrade() -> None:
    bind = op.get_bind()
    roles = _roles_table()
    user_roles = sa.Table(
        "sys_user_roles",
        sa.MetaData(),
        sa.Column("role_id", sa.BigInteger()),
    )

    role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.role_code == "ROLE_USER")
    ).scalar_one_or_none()
    if role_id is None:
        return

    user_count = bind.execute(
        sa.select(sa.func.count()).select_from(user_roles).where(user_roles.c.role_id == role_id)
    ).scalar_one()
    if user_count == 0:
        bind.execute(roles.delete().where(roles.c.id == role_id))
