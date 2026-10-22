"""Create the tasks table (owner and due date are added by later migrations).

Revision ID: 0bdbcb035215
Revises: 56be6b074842
"""

import sqlalchemy as sa
from alembic import op

revision = "0bdbcb035215"
down_revision = "56be6b074842"
branch_labels = None
depends_on = None


def _timestamp(name: str, comment: str) -> sa.Column:
    return sa.Column(
        name,
        sa.DateTime(),
        server_default=sa.func.now(),
        nullable=False,
        comment=comment,
    )


def upgrade() -> None:
    # SQLAlchemy stores enum members by name, so the database type is upper case.
    status = sa.Enum("CREATED", "IN_PROGRESS", "COMPLETED", name="taskstatus")
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, unique=True, comment="ID"),
        sa.Column("title", sa.String(), nullable=False, comment="Title"),
        sa.Column("description", sa.String(), comment="Description"),
        sa.Column("status", status, nullable=False, comment="Status"),
        _timestamp("created_at", "Created at"),
        _timestamp("updated_at", "Updated at"),
    )
    # users.id is already the primary key; the model also declares it unique.
    op.create_unique_constraint(None, "users", ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")  # type: ignore[arg-type]
    op.drop_table("tasks")
