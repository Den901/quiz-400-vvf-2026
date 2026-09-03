"""Tempi per singola domanda nella Sfida del giorno."""
from alembic import op
import sqlalchemy as sa

revision = "20260903_0010"
down_revision = "20260902_0009"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("daily_challenge_attempts", sa.Column("question_seconds", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("daily_challenge_attempts", "question_seconds")
