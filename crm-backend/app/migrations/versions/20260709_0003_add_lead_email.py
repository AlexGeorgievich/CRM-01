"""add email to leads

Revision ID: 20260709_0003
Revises: 20260708_0002
Create Date: 2026-07-09 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260709_0003"
down_revision: Union[str, None] = "20260708_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("email", sa.String(length=320), nullable=True))
    op.create_index("ix_leads_email", "leads", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_column("leads", "email")
