"""record privacy notice acknowledgements

Revision ID: 20260814_0002
Revises: 20260812_0001
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_0002"
down_revision = "20260812_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("privacy_policy_version", sa.String(length=40), nullable=True))
    op.add_column("users", sa.Column("privacy_acknowledged_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "privacy_acknowledged_at")
    op.drop_column("users", "privacy_policy_version")
