
"""Add profile photo path to user profiles."""

from alembic import op
import sqlalchemy as sa

revision = "0003_profile_photo"
down_revision = "0002_complaint_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("photo_path", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "photo_path")
