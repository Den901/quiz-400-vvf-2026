"""Schema cloud iniziale.

Revision ID: 20260812_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20260812_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        return
    op.create_table("settings", sa.Column("key", sa.String(80), primary_key=True), sa.Column("value", sa.JSON(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("username", sa.String(40), nullable=False), sa.Column("display_name", sa.String(100), nullable=False), sa.Column("email", sa.String(254), nullable=True), sa.Column("password_hash", sa.Text(), nullable=False), sa.Column("role", sa.String(10), nullable=False), sa.Column("active", sa.Boolean(), nullable=False), sa.Column("must_change_password", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True), sa.UniqueConstraint("username"), sa.UniqueConstraint("email"))
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_active", "users", ["active"])
    op.create_table("user_states", sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("data", sa.JSON(), nullable=False), sa.Column("revision", sa.Integer(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("login_sessions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ip_address", sa.String(64), nullable=False), sa.Column("user_agent", sa.String(300), nullable=False))
    op.create_index("ix_login_sessions_user_id", "login_sessions", ["user_id"])
    op.create_index("ix_login_sessions_token_hash", "login_sessions", ["token_hash"], unique=True)
    op.create_index("ix_login_sessions_expires_at", "login_sessions", ["expires_at"])
    op.create_table("password_resets", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_index("ix_password_resets_token_hash", "password_resets", ["token_hash"], unique=True)
    op.create_index("ix_password_resets_expires_at", "password_resets", ["expires_at"])
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("actor_user_id", sa.String(36), nullable=True), sa.Column("target_user_id", sa.String(36), nullable=True), sa.Column("action", sa.String(80), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("ip_address", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_target_user_id", "audit_logs", ["target_user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("password_resets")
    op.drop_table("login_sessions")
    op.drop_table("user_states")
    op.drop_table("users")
    op.drop_table("settings")
