"""forced daily challenge redo

Revision ID: 20260922_0013
Revises: 20260916_0012
Create Date: 2026-09-22
"""

from alembic import op
import sqlalchemy as sa


revision = "20260922_0013"
down_revision = "20260916_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("forced_challenge_date", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("forced_challenge_reason", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("forced_challenge_requested_by_user_id", sa.String(length=36), nullable=True))
    op.add_column("users", sa.Column("forced_challenge_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_forced_challenge_date", "users", ["forced_challenge_date"], unique=False)
    op.create_foreign_key(
        "fk_users_forced_challenge_requested_by",
        "users",
        "users",
        ["forced_challenge_requested_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_forced_challenge_requested_by", "users", type_="foreignkey")
    op.drop_index("ix_users_forced_challenge_date", table_name="users")
    op.drop_column("users", "forced_challenge_requested_at")
    op.drop_column("users", "forced_challenge_requested_by_user_id")
    op.drop_column("users", "forced_challenge_reason")
    op.drop_column("users", "forced_challenge_date")
