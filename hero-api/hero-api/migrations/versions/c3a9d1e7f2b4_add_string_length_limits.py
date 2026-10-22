"""add string length limits (Lab 1 validation rules)

Revision ID: c3a9d1e7f2b4
Revises: 611c902c525f
Create Date: 2026-10-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c3a9d1e7f2b4'
down_revision: Union[str, Sequence[str], None] = '611c902c525f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (table, column, new length) -- matches max_length in app/models.py
LIMITS = [
    ('team', 'name', 50),
    ('team', 'headquarters', 100),
    ('hero', 'name', 50),
    ('hero', 'secret_name', 50),
    ('hero', 'power', 100),
    ('mission', 'title', 100),
]


def upgrade() -> None:
    """Upgrade schema."""
    # batch mode so SQLite (no ALTER COLUMN) works too
    for table, column, length in LIMITS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(column,
                                  existing_type=sqlmodel.sql.sqltypes.AutoString(),
                                  type_=sqlmodel.sql.sqltypes.AutoString(length=length))


def downgrade() -> None:
    """Downgrade schema."""
    for table, column, length in LIMITS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(column,
                                  existing_type=sqlmodel.sql.sqltypes.AutoString(length=length),
                                  type_=sqlmodel.sql.sqltypes.AutoString())
