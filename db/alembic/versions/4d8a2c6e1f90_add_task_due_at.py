"""Add task due date

Revision ID: 4d8a2c6e1f90
Revises: 9c3e1f7a2b4d
Create Date: 2026-10-20 00:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4d8a2c6e1f90"
down_revision: Union[str, None] = "9c3e1f7a2b4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("due_at", sa.DateTime(), nullable=True, comment="Due at"),
    )


def downgrade() -> None:
    op.drop_column("tasks", "due_at")
