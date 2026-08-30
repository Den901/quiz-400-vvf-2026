"""Risposte alle segnalazioni e conferma di lettura per utente."""
from alembic import op
import sqlalchemy as sa

revision = "20260830_0008"
down_revision = "20260829_0007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("question_reports", sa.Column("reply", sa.Text(), nullable=True))
    op.add_column("question_reports", sa.Column("reply_read_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("question_reports", "reply_read_at")
    op.drop_column("question_reports", "reply")
