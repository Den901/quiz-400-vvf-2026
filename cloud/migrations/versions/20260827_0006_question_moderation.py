"""Aggiunge segnalazioni e moderazione dei quesiti.

Revision ID: 20260827_0006
Revises: 20260826_0005
"""

from alembic import op
import sqlalchemy as sa


revision = "20260827_0006"
down_revision = "20260826_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("reason", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_question_reports_question_id", "question_reports", ["question_id"])
    op.create_index("ix_question_reports_user_id", "question_reports", ["user_id"])
    op.create_index("ix_question_reports_status", "question_reports", ["status"])
    op.create_index("ix_question_reports_created_at", "question_reports", ["created_at"])
    op.create_table(
        "disabled_questions",
        sa.Column("question_id", sa.String(length=100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disabled_by_user_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["disabled_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("question_id"),
    )
    op.create_index("ix_disabled_questions_disabled_at", "disabled_questions", ["disabled_at"])


def downgrade() -> None:
    op.drop_index("ix_disabled_questions_disabled_at", table_name="disabled_questions")
    op.drop_table("disabled_questions")
    op.drop_index("ix_question_reports_created_at", table_name="question_reports")
    op.drop_index("ix_question_reports_status", table_name="question_reports")
    op.drop_index("ix_question_reports_user_id", table_name="question_reports")
    op.drop_index("ix_question_reports_question_id", table_name="question_reports")
    op.drop_table("question_reports")
