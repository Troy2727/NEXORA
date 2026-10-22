"""Add teams, members, invites and messages

Revision ID: c41d9e7b2a10
Revises: b7e3f2a91c55
Create Date: 2026-10-20 01:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c41d9e7b2a10"
down_revision: Union[str, None] = "b7e3f2a91c55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _id() -> sa.Column:
    return sa.Column(
        "id", sa.Integer(), autoincrement=True, nullable=False, comment="ID"
    )


def _created(comment: str = "Created at") -> sa.Column:
    return sa.Column(
        "created_at",
        sa.DateTime(),
        server_default=sa.text("now()"),
        nullable=False,
        comment=comment,
    )


def upgrade() -> None:
    op.create_table(
        "teams",
        _id(),
        sa.Column("name", sa.String(), nullable=False, comment="Name"),
        sa.Column("owner_id", sa.Integer(), nullable=False, comment="Owner ID"),
        _created(),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_teams_owner_id"), "teams", ["owner_id"])

    op.create_table(
        "team_members",
        _id(),
        sa.Column("team_id", sa.Integer(), nullable=False, comment="Team ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="User ID"),
        sa.Column(
            "role",
            sa.Enum("OWNER", "MEMBER", name="teamrole"),
            nullable=False,
            comment="Role",
        ),
        _created("Joined at"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_team_members_team_id"), "team_members", ["team_id"])

    op.create_table(
        "team_invites",
        _id(),
        sa.Column("team_id", sa.Integer(), nullable=False, comment="Team ID"),
        sa.Column("email", sa.String(), nullable=False, comment="Invited email"),
        sa.Column("invited_by", sa.Integer(), nullable=False, comment="Inviter ID"),
        _created(),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("team_id", "email"),
    )
    op.create_index(op.f("ix_team_invites_team_id"), "team_invites", ["team_id"])
    op.create_index(op.f("ix_team_invites_email"), "team_invites", ["email"])

    op.create_table(
        "messages",
        _id(),
        sa.Column("team_id", sa.Integer(), nullable=False, comment="Team ID"),
        sa.Column("user_id", sa.Integer(), nullable=True, comment="Sender ID"),
        sa.Column("body", sa.Text(), nullable=False, comment="Body"),
        _created(),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_messages_team_id"), "messages", ["team_id"])


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("team_invites")
    op.drop_table("team_members")
    op.drop_table("teams")
    sa.Enum(name="teamrole").drop(op.get_bind(), checkfirst=True)
