"""add role to employees

Revision ID: a1b2c3d4e5f6
Revises: 8d07d9d2ce2b
Create Date: 2026-07-03

"""

import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "8d07d9d2ce2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # добавляем колонку с server_default, чтобы существующие строки
    # получили роль operator; затем можно убрать default на уровне схемы
    op.add_column(
        "employees",
        sa.Column("role", sa.String(), nullable=False, server_default="operator"),
    )


def downgrade() -> None:
    op.drop_column("employees", "role")
