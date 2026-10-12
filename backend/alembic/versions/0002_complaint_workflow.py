"""Phase 3 complaint workflow safeguards."""
from alembic import op

revision = "0002_complaint_workflow"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Workflow tables are already created by the production baseline.
    # This revision intentionally has no schema changes; it versions the Phase 3 behavior.
    pass

def downgrade() -> None:
    pass
