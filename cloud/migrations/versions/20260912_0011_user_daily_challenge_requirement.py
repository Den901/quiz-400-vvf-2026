"""Obbligo Sfida del giorno configurabile per utente."""
from alembic import op
import sqlalchemy as sa

revision = "20260912_0011"
down_revision = "20260903_0010"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("daily_challenge_required", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    op.drop_column("users", "daily_challenge_required")
