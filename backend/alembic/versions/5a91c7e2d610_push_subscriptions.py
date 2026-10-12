
"""Add browser push subscriptions."""

from alembic import op
import sqlalchemy as sa

revision = "5a91c7e2d610"
down_revision = "32f4b997e679"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institute_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.Text(), nullable=False),
        sa.Column("auth", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.String(length=40), nullable=True),
        sa.Column("updated_at", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["institute_id"], ["institutes.id"]),
        sa.UniqueConstraint(
            "endpoint", name="uq_push_subscriptions_endpoint"
        ),
    )
    op.create_index(
        "ix_push_subscriptions_user",
        "push_subscriptions",
        ["institute_id", "user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_push_subscriptions_user",
        table_name="push_subscriptions",
    )
    op.drop_table("push_subscriptions")
