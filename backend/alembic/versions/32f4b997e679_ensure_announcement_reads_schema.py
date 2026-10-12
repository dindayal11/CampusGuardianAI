"""ensure_announcement_reads_schema
Revision ID: 32f4b997e679
Revises: 48f8b7f64465
Create Date: 2026-10-11 17:59:19.244545
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '32f4b997e679'
down_revision: Union[str, Sequence[str], None] = '48f8b7f64465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    pass
def downgrade() -> None:
    pass
