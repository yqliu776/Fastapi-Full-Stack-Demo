"""Add status column to sys_users

Revision ID: 20260806_0001
Revises: 20260805_0001
Create Date: 2026-08-06 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260806_0001"
down_revision: Union[str, Sequence[str], None] = "20260805_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sys_users",
        sa.Column(
            "status",
            sa.String(length=1),
            nullable=False,
            server_default="N",
            comment="状态，N启用/Y禁用",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sys_users", "status")
