"""Create the users table.

Revision ID: 56be6b074842
Revises: (none, first migration)
"""

import sqlalchemy as sa
from alembic import op

revision = "56be6b074842"
down_revision = None
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
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, unique=True, comment="ID"),
        sa.Column("first_name", sa.String(), comment="First name"),
        sa.Column("last_name", sa.String(), comment="Last name"),
        sa.Column("email", sa.String(), nullable=False, comment="Email"),
        sa.Column("hashed_password", sa.String(), comment="Hashed password"),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="Is active"),
        sa.Column("last_login", sa.DateTime(), comment="Last login"),
        _timestamp("created_at", "Created at"),
    )


def downgrade() -> None:
    op.drop_table("users")
