"""Approvazione amministrativa dei nuovi account.

Revision ID: 20260817_0003
Revises: 20260814_0002
"""

from alembic import op
import sqlalchemy as sa


revision = "20260817_0003"
down_revision = "20260814_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "approved" not in columns:
        op.add_column("users", sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.true()))
        op.create_index("ix_users_approved", "users", ["approved"])
    op.execute(sa.text("UPDATE users SET approved = true WHERE approved IS NULL"))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "approved" in columns:
        indexes = {index["name"] for index in inspector.get_indexes("users")}
        if "ix_users_approved" in indexes:
            op.drop_index("ix_users_approved", table_name="users")
        op.drop_column("users", "approved")
