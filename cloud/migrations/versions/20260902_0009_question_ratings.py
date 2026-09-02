"""Valutazione comunitaria della difficoltà dei quesiti."""
from alembic import op
import sqlalchemy as sa

revision = "20260902_0009"
down_revision = "20260830_0008"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "question_ratings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 3", name="ck_question_rating_range"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "user_id", name="uq_question_rating_user"),
    )
    op.create_index("ix_question_ratings_question_id", "question_ratings", ["question_id"])
    op.create_index("ix_question_ratings_user_id", "question_ratings", ["user_id"])

def downgrade():
    op.drop_index("ix_question_ratings_user_id", table_name="question_ratings")
    op.drop_index("ix_question_ratings_question_id", table_name="question_ratings")
    op.drop_table("question_ratings")
