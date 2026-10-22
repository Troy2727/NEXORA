"""Add task owner

Revision ID: 9c3e1f7a2b4d
Revises: 0bdbcb035215
Create Date: 2026-10-19 23:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9c3e1f7a2b4d"
down_revision: Union[str, None] = "0bdbcb035215"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("user_id", sa.Integer(), nullable=True, comment="Owner ID"),
    )
    # Tasks created before ownership existed go to the first registered user.
    op.execute("UPDATE tasks SET user_id = (SELECT MIN(id) FROM users)")
    # Only possible when no users exist at all, so these tasks were unreachable.
    op.execute("DELETE FROM tasks WHERE user_id IS NULL")
    op.alter_column("tasks", "user_id", nullable=False)
    op.create_index(op.f("ix_tasks_user_id"), "tasks", ["user_id"])
    op.create_foreign_key(
        "fk_tasks_user_id_users",
        "tasks",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_user_id_users", "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_user_id"), table_name="tasks")
    op.drop_column("tasks", "user_id")
