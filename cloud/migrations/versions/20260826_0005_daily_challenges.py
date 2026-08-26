"""Aggiunge la Sfida del giorno e la relativa classifica.

Revision ID: 20260826_0005
Revises: 20260817_0004
"""

from alembic import op
import sqlalchemy as sa


revision = "20260826_0005"
down_revision = "20260817_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_challenges",
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("composition", sa.JSON(), nullable=False),
        sa.Column("app_version", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("challenge_date"),
    )
    op.create_table(
        "daily_challenge_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("challenge_date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correct", sa.Integer(), nullable=True),
        sa.Column("wrong", sa.Integer(), nullable=True),
        sa.Column("blank", sa.Integer(), nullable=True),
        sa.Column("score_x100", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_date"], ["daily_challenges.challenge_date"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("challenge_date", "user_id", name="uq_daily_challenge_attempt_user_date"),
    )
    op.create_index("ix_daily_challenge_attempts_challenge_date", "daily_challenge_attempts", ["challenge_date"])
    op.create_index("ix_daily_challenge_attempts_user_id", "daily_challenge_attempts", ["user_id"])
    op.create_index("ix_daily_challenge_attempts_submitted_at", "daily_challenge_attempts", ["submitted_at"])
    op.create_index("ix_daily_challenge_attempts_score_x100", "daily_challenge_attempts", ["score_x100"])


def downgrade() -> None:
    op.drop_index("ix_daily_challenge_attempts_score_x100", table_name="daily_challenge_attempts")
    op.drop_index("ix_daily_challenge_attempts_submitted_at", table_name="daily_challenge_attempts")
    op.drop_index("ix_daily_challenge_attempts_user_id", table_name="daily_challenge_attempts")
    op.drop_index("ix_daily_challenge_attempts_challenge_date", table_name="daily_challenge_attempts")
    op.drop_table("daily_challenge_attempts")
    op.drop_table("daily_challenges")
