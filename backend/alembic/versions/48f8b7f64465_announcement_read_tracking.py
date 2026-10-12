"""announcement_read_tracking
Revision ID: 48f8b7f64465
Revises: 0003_profile_photo
Create Date: 2026-10-11 17:56:00.172933
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '48f8b7f64465'
down_revision: Union[str, Sequence[str], None] = '0003_profile_photo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "announcement_reads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("announcement_id", sa.Integer(), nullable=False),
        sa.Column("institute_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("read_at", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(
            ["announcement_id"],
            ["announcements.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["institute_id"],
            ["institutes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "announcement_id",
            "user_id",
            name="uq_announcement_read_user",
        ),
    )
    op.create_index(
        "ix_announcement_reads_user",
        "announcement_reads",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_announcement_reads_user",
        table_name="announcement_reads",
    )
    op.drop_table("announcement_reads")

