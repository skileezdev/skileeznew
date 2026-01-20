"""Add contract acceptance and message type fields

Revision ID: 006
Revises: 005
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to contract table
    op.add_column('contract', sa.Column('accepted_at', sa.DateTime(), nullable=True))
    op.add_column('contract', sa.Column('declined_at', sa.DateTime(), nullable=True))
    op.add_column('contract', sa.Column('payment_completed_at', sa.DateTime(), nullable=True))
    
    # Update contract status default to 'pending'
    op.execute("UPDATE contract SET status = 'pending' WHERE status = 'active'")
    
    # Add message_type field to message table
    op.add_column('message', sa.Column('message_type', sa.String(20), nullable=True, server_default='TEXT'))


def downgrade():
    # Remove message_type field from message table
    op.drop_column('message', 'message_type')
    
    # Remove new fields from contract table
    op.drop_column('contract', 'payment_completed_at')
    op.drop_column('contract', 'declined_at')
    op.drop_column('contract', 'accepted_at')
