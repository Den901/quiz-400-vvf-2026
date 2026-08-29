"""Aggiunge le foto profilo degli utenti.

Revision ID: 20260829_0007
Revises: 20260827_0006
"""

from alembic import op
import sqlalchemy as sa


revision = "20260829_0007"
down_revision = "20260827_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_avatars",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("mime", sa.String(length=20), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_avatars")
