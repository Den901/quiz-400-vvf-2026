"""Visibilità del monitor delle prove attive per account."""
from alembic import op
import sqlalchemy as sa


revision = "20260916_0012"
down_revision = "20260912_0011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("active_challenge_monitor_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade():
    op.drop_column("users", "active_challenge_monitor_enabled")
