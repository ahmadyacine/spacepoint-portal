"""update user role enum

Revision ID: 23a194699305
Revises: 4c5ed551ae6d
Create Date: 2026-03-10 04:21:33.475871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23a194699305'
down_revision: Union[str, Sequence[str], None] = '4c5ed551ae6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the new enum value directly to PostgreSQL
    op.execute("ALTER TYPE userrole ADD VALUE 'FACILITATOR'")

def downgrade() -> None:
    # Postgres doesn't easily support dropping an enum value.
    pass
