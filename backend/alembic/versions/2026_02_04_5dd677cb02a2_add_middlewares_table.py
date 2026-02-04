"""add_middlewares_table

Revision ID: 5dd677cb02a2
Revises: 83600d5d28fa
Create Date: 2026-02-04 18:57:55.141441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Идентификаторы ревизии
revision: str = '5dd677cb02a2'
down_revision: Union[str, None] = '83600d5d28fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Применение миграции."""
    op.create_table(
        'middlewares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('middleware_type', sa.String(length=20), nullable=False, server_default='both'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_middlewares_is_active'), 'middlewares', ['is_active'], unique=False)
    op.create_index(op.f('ix_middlewares_name'), 'middlewares', ['name'], unique=True)
    op.create_index(op.f('ix_middlewares_order'), 'middlewares', ['order'], unique=False)


def downgrade() -> None:
    """Откат миграции."""
    op.drop_index(op.f('ix_middlewares_order'), table_name='middlewares')
    op.drop_index(op.f('ix_middlewares_name'), table_name='middlewares')
    op.drop_index(op.f('ix_middlewares_is_active'), table_name='middlewares')
    op.drop_table('middlewares')
