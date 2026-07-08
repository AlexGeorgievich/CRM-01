"""add next contact date to leads

Revision ID: 20260708_0002
Revises: 20260708_0001
Create Date: 2026-07-08 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260708_0002"
down_revision: Union[str, None] = "20260708_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("next_contact_date", sa.Date(), nullable=True))
    op.create_index("ix_leads_next_contact_date", "leads", ["next_contact_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_next_contact_date", table_name="leads")
    op.drop_column("leads", "next_contact_date")
