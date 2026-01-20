"""Add call_id to message table

Revision ID: 011
Revises: 010
Create Date: 2024-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

def upgrade():
    # Add call_id column to message table
    op.add_column('message', sa.Column('call_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_message_call_id', 'message', 'scheduled_call', ['call_id'], ['id'])
    op.create_index(op.f('ix_message_call_id'), 'message', ['call_id'], unique=False)

def downgrade():
    # Remove call_id column from message table
    op.drop_index(op.f('ix_message_call_id'), table_name='message')
    op.drop_constraint('fk_message_call_id', 'message', type_='foreignkey')
    op.drop_column('message', 'call_id')
