"""Add contract payment fields

Revision ID: 005
Revises: 004
Create Date: 2024-08-18 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    """Add payment fields to contract table"""
    # Add payment fields to contract table
    op.add_column('contract', sa.Column('payment_status', sa.String(20), nullable=False, server_default='pending'))
    op.add_column('contract', sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True))
    op.add_column('contract', sa.Column('payment_date', sa.DateTime(), nullable=True))
    
    # Create index on payment_status for faster queries
    op.create_index('ix_contract_payment_status', 'contract', ['payment_status'])
    
    # Create index on stripe_payment_intent_id for webhook processing
    op.create_index('ix_contract_stripe_payment_intent_id', 'contract', ['stripe_payment_intent_id'])

def downgrade():
    """Remove payment fields from contract table"""
    # Drop indexes
    op.drop_index('ix_contract_stripe_payment_intent_id', 'contract')
    op.drop_index('ix_contract_payment_status', 'contract')
    
    # Drop columns
    op.drop_column('contract', 'payment_date')
    op.drop_column('contract', 'stripe_payment_intent_id')
    op.drop_column('contract', 'payment_status')
