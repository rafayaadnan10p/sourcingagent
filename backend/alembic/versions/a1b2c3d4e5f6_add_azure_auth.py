"""add azure auth fields to users table

Revision ID: a1b2c3d4e5f6
Revises: cd5010d36f34
Create Date: 2026-07-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cd5010d36f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make hashed_password nullable (Microsoft auth users have no password)
    op.alter_column('users', 'hashed_password', nullable=True)
    # Add Azure Object ID — unique identifier from Microsoft, used for login lookup
    op.add_column('users', sa.Column('azure_oid', sa.String(255), nullable=True))
    op.create_unique_constraint('uq_users_azure_oid', 'users', ['azure_oid'])


def downgrade() -> None:
    op.drop_constraint('uq_users_azure_oid', 'users', type_='unique')
    op.drop_column('users', 'azure_oid')
    op.alter_column('users', 'hashed_password', nullable=False)
